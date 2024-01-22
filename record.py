import datetime
import io
import pickle
import uuid


class RecordBase:
    def __init__(self):
        self.timestamp = datetime.datetime.today()
        self.id = None

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


class Audio2TextRecord(RecordBase):
    def __init__(self, ident, raw_audio_byte, audio2text):
        super().__init__()
        self.id = ident
        self.raw_audio_byte = raw_audio_byte
        self.audio2text = audio2text


class Text2AdviceRecord(RecordBase):
    def __init__(self, ident, in_text, advice_text):
        super().__init__()
        self.id = ident
        self.in_text = in_text
        self.advice_text = advice_text


class Advice2SummaryRecord(RecordBase):
    # advice_texts is array of string(advice text array)
    # summary_text is basically a single string text
    def __init__(self, ident, advice_texts, summary_text):
        super().__init__()
        # TODO: refactor me! this must be written in base class __init__
        if ident is None:
            ident = str(uuid.uuid4())

        self.id = ident
        self.advice_texts = advice_texts
        self.summary_text = summary_text


class LLMInstanceRecord(RecordBase):
    def __init__(self, ident, instruction, input_):
        super().__init__()
        self.id = ident
        self.instruction = instruction
        self.input_ = input_
        self.result = None
