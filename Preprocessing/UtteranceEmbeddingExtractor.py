import os

import torch
import torch.multiprocessing

from EmbeddingModel.StyleEmbedding import StyleEmbedding
from Preprocessing.AudioPreprocessor import AudioPreprocessor
from Utility.storage_config import MODELS_DIR


class ProsodicConditionExtractor:

    def __init__(self, sr, device=torch.device("cpu"), path_to_model=os.path.join(MODELS_DIR, "Embedding", "embedding_function.pt")):
        self.ap = AudioPreprocessor(input_sr=sr, output_sr=16000, cut_silence=False)
        self.embed = StyleEmbedding()
        check_dict = torch.load(path_to_model, map_location="cpu")
        self.embed.load_state_dict(check_dict["style_emb_func"])
        self.embed.to(device)
        self.sr = sr
        self.device = device

    def extract_condition_from_reference_wave(self, wave, already_normalized=False):
        if already_normalized:
            norm_wave = wave
        else:
            norm_wave = self.ap.normalize_audio(audio=wave)
        spec = self.ap.audio_to_mel_spec_tensor(norm_wave, explicit_sampling_rate=self.sr).transpose(0, 1)
        spec_batch = torch.stack([spec] * 5, dim=0)
        spec_len_batch = torch.LongTensor([len(spec)] * 5)
        return torch.mean(self.embed(spec_batch.to(self.device), spec_len_batch.to(self.device)), dim=0).squeeze()
