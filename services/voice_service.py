import os
import asyncio
import edge_tts
import shutil

# Lazy imports for heavy ML libraries to allow lean production builds
torch = None
se_extractor = None
ToneColorConverter = None

class VoiceService:
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Paths for OpenVoice
        self.ckpt_dir = os.path.join(self.base_dir, "OpenVoice", "checkpoints_v2", "checkpoints_v2")
        self.converter_config = os.path.join(self.ckpt_dir, "converter", "config.json")
        self.converter_ckpt = os.path.join(self.ckpt_dir, "converter", "checkpoint.pth")
        
        # Audio Paths
        self.reference_voice = os.path.join(self.base_dir, 'static', 'audio', 'guruji_voice.wav')
        self.processed_dir = os.path.join(self.base_dir, 'static', 'audio', 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Model State (Init as CPU, upgrade to CUDA if torch is found later)
        self.device = "cpu"
        self.converter = None
        self.target_se = None
        self.source_se = None # Optimized: Cache source SE too
        
        # Pre-load model
        self._initialize_models()

    def _initialize_models(self):
        """Loads the local OpenVoice converter and extracts speaker prints."""
        global torch, se_extractor, ToneColorConverter
        try:
            # Try to import heavy dependencies only when needed
            if torch is None:
                import torch as _torch
                torch = _torch
                # Update device once torch is loaded
                if torch.cuda.is_available():
                    self.device = "cuda"
            if se_extractor is None:
                from openvoice import se_extractor as _se
                se_extractor = _se
            if ToneColorConverter is None:
                from openvoice.api import ToneColorConverter as _api
                ToneColorConverter = _api

            if not os.path.exists(self.converter_config):
                print("ℹ️ OpenVoice checkpoints not found. Local cloning disabled.")
                return

            print(f"🎙️ Initializing Local Voice Engine on {self.device}...")
            self.converter = ToneColorConverter(self.converter_config, device=self.device, enable_watermark=False)
            self.converter.load_ckpt(self.converter_ckpt)
            
            # 1. Load/Extract Guruji's Tone Print
            se_path = os.path.join(self.processed_dir, 'guruji_se.pth')
            if os.path.exists(se_path):
                self.target_se = torch.load(se_path, map_location=self.device)
                print("✅ Guruji tone print loaded")
            elif os.path.exists(self.reference_voice):
                print("⚙️ Extracting Guruji tone print...")
                self.target_se, _ = se_extractor.get_se(self.reference_voice, self.converter, target_dir=self.processed_dir, vad=True)
                torch.save(self.target_se, se_path)
            
            # 2. Optimized: Pre-extract Source Tone Print (for hi-IN-MadhurNeural)
            # Since we always use the same base voice, we only need to extract its SE once!
            source_se_path = os.path.join(self.processed_dir, 'madhur_source_se.pth')
            if os.path.exists(source_se_path):
                self.source_se = torch.load(source_se_path, map_location=self.device)
                print("✅ Base voice print loaded")
            else:
                print("⚙️ Calibrating base voice print (one-time)...")
                sample_path = os.path.join(self.processed_dir, "calibration_sample_v3.wav")
                async def create_sample():
                    # Long enough for V2 extractor
                    calibration_text = "बेटा, जय श्री श्याम। आपके जीवन में सुख, शांति और समृद्धि हमेशा बनी रहे। बाबा श्याम का आशीर्वाद आप पर सदा बना रहे।"
                    c = edge_tts.Communicate(calibration_text, "hi-IN-MadhurNeural")
                    await c.save(sample_path)
                
                try:
                    import threading
                    def run_async_safe():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        new_loop.run_until_complete(create_sample())
                        new_loop.close()
                    
                    t = threading.Thread(target=run_async_safe)
                    t.start()
                    t.join()
                        
                    if os.path.exists(sample_path):
                        # Force VAD=False for clean TTS to be faster and more reliable
                        self.source_se, _ = se_extractor.get_se(sample_path, self.converter, target_dir=self.processed_dir, vad=False)
                        torch.save(self.source_se, source_se_path)
                        os.remove(sample_path)
                        print("✅ Base voice print calibrated (High Speed Mode)")
                    else:
                        print("❌ Calibration failed: file not created")
                except Exception as ex:
                    print(f"⚠️ Calibration failed: {ex}")

        except Exception as e:
            print(f"❌ Voice Engine Init Error: {e}")

    async def generate_voice(self, text: str, output_path: str) -> bool:
        """
        Generates Guruji's voice:
        1. Base Hindi via Edge-TTS
        2. Tone Conversion via OpenVoice
        Output: WAV file at output_path
        """
        if not self.converter or self.target_se is None:
            self._initialize_models()
            if not self.converter: return False

        base_name = os.path.basename(output_path).replace(".wav", "").replace(".mp3", "")
        temp_base_path = os.path.join(self.processed_dir, f"temp_{base_name}.mp3")
        
        try:
            # Step 1: Generate base Hindi audio via Edge-TTS
            communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
            await communicate.save(temp_base_path)
            
            # Step 2: Tone conversion (OpenVoice cloning)
            curr_source_se = self.source_se
            if curr_source_se is None:
                curr_source_se, _ = se_extractor.get_se(
                    temp_base_path, self.converter,
                    target_dir=self.processed_dir, vad=False
                )
            
            self.converter.convert(
                audio_src_path=temp_base_path,
                src_se=curr_source_se,
                tgt_se=self.target_se,
                output_path=output_path,
                tau=0.3
            )
            
            if os.path.exists(output_path):
                print(f"✅ Voice output saved: {output_path}")
                return True
            else:
                print(f"❌ Converter did not produce output at: {output_path}")
                return False

        except Exception as e:
            print(f"❌ Local Voice Generation Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if os.path.exists(temp_base_path):
                try: os.remove(temp_base_path)
                except: pass

voice_service = VoiceService()
