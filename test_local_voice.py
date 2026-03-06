import os
import torch
import torch.hub
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

def test_local_setup():
    print("--- Testing Local Setup ---")
    
    # Check paths
    base_dir = r"c:\Users\prava\OneDrive\Desktop\yantra\backend"
    ckpt_dir = os.path.join(base_dir, "OpenVoice", "checkpoints_v2", "checkpoints_v2")
    converter_config = os.path.join(ckpt_dir, "converter", "config.json")
    converter_ckpt = os.path.join(ckpt_dir, "converter", "checkpoint.pth")
    
    print(f"Checking OpenVoice Checkpoints:")
    print(f"Config: {os.path.exists(converter_config)}")
    print(f"Ckpt: {os.path.exists(converter_ckpt)}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    try:
        print("Loading ToneColorConverter (Watermark Disabled)...")
        converter = ToneColorConverter(converter_config, device=device, enable_watermark=False)
        converter.load_ckpt(converter_ckpt)
        print("✅ ToneColorConverter loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load ToneColorConverter: {e}")
        return

    try:
        import edge_tts
        import asyncio
        
        print("--- Testing Hybrid Local Flow ---")
        test_text = "बेटा, जय श्री श्याम। श्री श्याम यंत्र की कृपा आप पर बनी रहे।"
        
        # 1. Generate Base Audio with edge-tts (Hindi)
        print("Step 1: Generating base audio with edge-tts...")
        base_audio_path = "base_hindi.mp3"
        voice = "hi-IN-MadhurNeural"
        communicate = edge_tts.Communicate(test_text, voice)
        asyncio.run(communicate.save(base_audio_path))
        print("✅ Base audio generated")
        
        # 2. Extract SE (Tone Color) from Guruji source
        print("Step 2: Extracting Guruji Tone Color...")
        ref_voice = r"static\audio\guruji_voice.wav"
        if not os.path.exists(ref_voice):
            print(f"❌ Reference voice missing at {ref_voice}")
            return
            
        target_se, r_spec = se_extractor.get_se(ref_voice, converter, target_dir='processed', vad=True)
        print("✅ Guruji Tone extracted")
        
        # 3. Convert (Tone Swap)
        print("Step 3: Converting tone to Guruji's voice...")
        # Since edge-tts is mp3, we might need a wav for OpenVoice or just pass it
        # OpenVoice handles path loading.
        output_path = "guruji_cloned_local.wav"
        
        # We need a source SE. For conversion, we can usually use a default or extract from source.
        # But for 'color swap', you often extract SE from the source audio itself.
        source_se, s_spec = se_extractor.get_se(base_audio_path, converter, target_dir='processed', vad=True)
        
        converter.convert(
            audio_src_path=base_audio_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=output_path,
            tau=0.3
        )
        print(f"✅ FINAL CLONED VOICE GENERATED: {output_path}")

    except Exception as e:
        import traceback
        print(f"❌ Failed Local Flow: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_local_setup()
