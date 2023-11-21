import subprocess
import tempfile
import glob
import os
import time
import shutil

tmpdir = tempfile._get_default_tempdir()

def run(*args):
    return subprocess.check_output(*args)

def cleanup(delta=300):
    files = glob.glob(tmpdir+"/loopli*.wav")
    for f in files:
        mtime = os.path.getmtime(f)
        if time.time() - mtime > delta:
            os.remove(f)

cleanup()

class Wav:

    def __init__(self, file):
        self.file = file
        self._len = None

    def len(self):
        if not self._len:
            self._len = float(run(["soxi","-D",self.file]))
        return self._len

    def baselen(self):
        len = self.len()
        return 4 if len <= 4 else 8 if len <= 8 else 16

    def bpm(self):
        len = self.len()
        return 120 / len * self.baselen()

    def tmpf():
        fname = 'looplipy_' + next(tempfile._get_candidate_names()) + '.wav'
        return tmpdir+ "/" + fname

    def mod(self, mods):
        tmpf = self.__class__.tmpf()
        run(["sox", self.file, tmpf, *mods.strip().split(" ")])
        return self.__class__(tmpf)

    def resize(self, new_len):
        return self.mod('speed %f ' % (self.len()/new_len) )

    def resize_bpm(self,new_bpm):
        return self.resize(120 * self.baselen() / new_bpm)

    def round_bpm(self):
        bpm = self.bpm()
        return self.resize_bpm(round(bpm)) if not bpm.is_integer() else self

    def __getattr__(self,prop):
        return lambda *args : self.mod(prop + " " + " ".join(args))

    def save(dest):
        shutil.copy(this.file, dest)

