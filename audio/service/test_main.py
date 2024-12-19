from fastapi.testclient import TestClient
from .main import app
import numpy as np

client = TestClient(app)

def test_transcriptions():
    urls = [
        'https://github.com/ryanjeffares/test-audio-files/raw/refs/heads/main/C_01_CHOP_FA.wav',
        'https://github.com/ryanjeffares/test-audio-files/raw/refs/heads/main/C_05_ECHO_FG.wav',
        'https://github.com/ryanjeffares/test-audio-files/raw/refs/heads/main/C_08_NOISE_ML.wav',
        'https://github.com/ryanjeffares/test-audio-files/raw/refs/heads/main/C_14_CLIP_ML.wav',
    ]

    transcriptions = [
        "It's easy to tell the depth of a well. The juice of lemons makes fine punch.",
        "Grape juice and water mix well. Soap can wash most dirt away.",
        "The mail comes in three batches per day. Open your book to the first page.",
        "A stuffed chair slipped from the moving van. Open your book to the first page.",
    ]

    for url in urls:
        response = client.post(f'/transcriptions?audiofile_url={url}')
        assert response.status_code == 200
    
    for i in range(4):
        transcription_id = str(i)
        response = client.get(f'/transcriptions/{transcription_id}')
        assert response.status_code == 200
        prediction = ''.join(t['text'] for t in response.json())
        assert wer(transcriptions[i], prediction) <= 0.05


def wer(reference: str, prediction: str) -> float:
    ref_words = reference.split()
    hyp_words = prediction.split()
    
    # Lengths of the sentences
    n = len(ref_words)
    m = len(hyp_words)
    
    # Create a (n+1) x (m+1) matrix
    dp = np.zeros((n+1, m+1), dtype=np.int32)
    
    # Initialize the matrix
    for i in range(n+1):
        dp[i][0] = i  # Deletion cost
    for j in range(m+1):
        dp[0][j] = j  # Insertion cost
    
    # Fill the matrix
    for i in range(1, n+1):
        for j in range(1, m+1):
            if ref_words[i-1] == hyp_words[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No error
            else:
                substitution = dp[i-1][j-1] + 1
                insertion = dp[i][j-1] + 1
                deletion = dp[i-1][j] + 1
                dp[i][j] = min(substitution, insertion, deletion)
    
    # The edit distance
    edit_distance = dp[n][m]
    
    # Calculate the WER
    wer = edit_distance / n
    return wer
