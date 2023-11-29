import datetime
import io
import pickle


class RecordBase:
    def __init__(self):
        self.timestamp = datetime.datetime.today()

    @classmethod
    def to_byte(cls, obj):
        bytes_io = io.BytesIO()
        pickle.dump(obj, bytes_io)
        byte_data = bytes_io.getvalue()
        return byte_data

    @classmethod
    def from_byte(cls, byte_data):
        bytes_io = io.BytesIO(byte_data)
        loaded_object = pickle.load(bytes_io)
        return loaded_object


class RawAudioRecord(RecordBase):
    def __init__(self, raw_audio_byte):
        super().__init__()
        self.raw_audio_byte = raw_audio_byte
