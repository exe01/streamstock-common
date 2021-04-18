from .model import Model
from .const import *


class PipelineSettings(Model):
    API_NAME = 'pipeline_settings'
    TIMEDELTA_FIELDS = [
        TWITCH_CHAT_SKIP,
        AVG_HIGHLIGHTS_TIC,
        AVG_HIGHLIGHTS_SKIP_CALC,
        SPEECH_DETECTOR_MAX_OF_SILENCE,
        SPEECH_DETECTOR_ADDITIONAL_BEGIN,
        SPEECH_DETECTOR_ADDITIONAL_END,
    ]

    def __init__(self, representation):
        super().__init__(representation)

    def update_timedelta_fields(self):
        pass
