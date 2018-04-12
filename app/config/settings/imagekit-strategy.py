class FixJustInTime:
    def on_content_required(self, file):
        try:
            file.generate()
        except:
            pass

    def on_existence_required(self, file):
        try:
            file.generate()
        except:
            pass
