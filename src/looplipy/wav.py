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
        self._bpm = None

    def len(self):
        if not self._len:
            self._len = float(run(["soxi","-D",self.file]))
        return self._len

    def baselen(self):
        len = self.len()
        return 4 if len <= 4 else 8 if len <= 8 else 16

    def bpm(self):
        if not self._bpm:
            len = self.len()
            self._bpm = 120 / len * self.baselen()
        return self._bpm

    def tmpf(ext='wav'):
        fname = 'looplipy_' + next(tempfile._get_candidate_names()) + '.' + ext
        return tmpdir+ "/" + fname

    def mod(self, mods):
        tmpf = self.__class__.tmpf()
        run(["sox", self.file, tmpf, *mods.strip().split(" ")])
        return self.__class__(tmpf)

    def resize(self, new_len):
        return self.mod('speed %f ' % (self.len()/new_len) )

    def resize_bpm(self,new_bpm):
        obj = self.resize(120 * self.baselen() / new_bpm)
        obj._bpm = new_bpm
        return obj

    def round_bpm(self):
        bpm = self.bpm()
        return self.resize_bpm(round(bpm)) if not bpm.is_integer() else self

    def __getattr__(self,prop):
        return lambda *args : self.mod(prop + " " + " ".join(args))

    def play(self):
        run(["play", self.file])

    def mp3(self):
        tmpf = self.__class__.tmpf('mp3')
        run(['sox',self.file,'-C','320',tmpf])
        return self.__class__(tmpf)

    def wrap(wav):
        return wav if isinstance(wav, __class__) else __class__(wav)

    def join(*wavs):
        args = ['sox']
        args.extend([__class__.wrap(w).file for w in wavs])
        tmpf = __class__.tmpf()
        args.append(tmpf)
        run(args)
        return __class__(tmpf)

    def save(dest):
        shutil.copy(this.file, dest)

