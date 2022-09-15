import json

class ProjectSettings:
    def __init__(self):
        self.gfam_version = str
        self.input_video = str
        self.working_dir = str
        self.js_path = str
        self.exif_config = str
        self.filter_telemetry = bool
        self.scale_factor = float
        self.frame_sample_freq = int
        self.overwrite = bool
        pass

    def applySettings(self, json):
        self.gfam_version = json['gfam_version']
        self.input_video = json['input_video_dir']
        self.working_dir = json['working_dir']
        self.filter_telemetry = json['filter_telemetry']
        self.scale_factor = json['scale_factor']
        self.frame_sample_freq = json['frame_sample_freq']
        self.overwrite = json['overwrite']

    def importSettings(self, input):
        with open(input) as f:
            settings = json.load(f)
            self.applySettings(settings)

    def asdict(self):
        return {'gfam_version': self.gfam_version,
                'input_video': self.input_video,
                'working_dir': self.working_dir,
                'filter_telemetry': self.filter_telemetry,
                'minimum_radius': self.minimum_radius,
                'scale_factor': self.scale_factor,
                'frame_sample_freq': self.frame_sample_freq,
                'overwrite': self.overwrite}

    def returnSettings(self):
        s = self.asdict()
        return(s)

    def exportSettings(self, output):
        settings = self.asdict()
        with open(output, 'w') as f:
            json.dump(settings, f, indent=4)

class Project:
    def __init__(self, name):
        self.name = name
        self.settings = ProjectSettings

    def importSettings(self, json_path):
        self.settings.ApplySettings(json_path)

    def exportSettings(self, json_path):
        self.settings.exportSettings(json_path)

    

