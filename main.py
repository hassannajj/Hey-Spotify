from re import L
import requests
import sys
from api_secrets import API_KEY_ASSEMBLYAI

headers = {'authorization':  API_KEY_ASSEMBLYAI}
audio_filename = sys.argv[1]

# endpoints
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"


# upload
def upload(audio_filename):

    def read_file(audio_filename, chunk_size=5242880):
        with open(audio_filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint,
                            headers=headers,
                            data=read_file(audio_filename))


    audio_url = upload_response.json()['upload_url']
    return audio_url


# transcribe
def transcribe(audio_url):
        
    transcript_request = { "audio_url": audio_url }
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    
    job_id = transcript_response.json()['id']
    return job_id



# poll
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response


def get_transcription_results_url(transcript_id):
    while True:
        polling_response = poll(transcript_id)
        status = polling_response.json()['status']
        if status == "completed":
            return polling_response.json()
        elif status == "error":
            return "error"




# save transcript
def save_transcript(data):

    text_filename = audio_filename + ".txt"
    with open(text_filename, 'w') as f:
        f.write(data['text'])
    print("Transcription saved")





def main():
    audio_url = upload(audio_filename)
    transcript_id = transcribe(audio_url)
    data = get_transcription_results_url(transcript_id)
    if data != "error":
        save_transcript(data)
    else:
        print("Error: failed to obtain transcription")




if __name__ == "__main__":
    main()