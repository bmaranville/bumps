from .. import monitor
from ..formatnum import format_uncertainty
from ..fitproblem import nllf_scale

class WebConsoleMonitor(monitor.TimedUpdate):
    """
    Display fit progress on the console
    """
    def __init__(self, problem, progress=1, improvement=30):
        monitor.TimedUpdate.__init__(self, progress=progress,
                                     improvement=improvement)
        self.problem = problem

    def show_progress(self, history):
        scale, err = nllf_scale(self.problem)
        chisq = format_uncertainty(scale*history.value[0], err)
        print("step", history.step[0], "cost", chisq)
        sys.stdout.flush()

    def show_improvement(self, history):
        # print "step",history.step[0],"chisq",history.value[0]
        p = self.problem.getp()
        try:
            self.problem.setp(history.point[0])
            print(self.problem.summarize())
        finally:
            self.problem.setp(p)
        sys.stdout.flush()


class WebStepMonitor(monitor.Monitor):
    """
    Collect information at every step of the fit and save it to a file.

    *fid* is the file to save the information to
    *fields* is the list of "step|time|value|point" fields to save

    The point field should be last in the list.
    """
    FIELDS = ['step', 'time', 'value', 'point']

    def __init__(self, problem, fid, fields=FIELDS):
        if any(f not in self.FIELDS for f in fields):
            raise ValueError("invalid monitor field")
        self.fid = fid
        self.fields = fields
        self.problem = problem
        self._pattern = "%%(%s)s\n" % (")s %(".join(fields))
        fid.write("# " + ' '.join(fields) + '\n')

    def config_history(self, history):
        history.requires(time=1, value=1, point=1, step=1)

    def __call__(self, history):
        point = " ".join("%.15g" % v for v in history.point[0])
        time = "%g" % history.time[0]
        step = "%d" % history.step[0]
        scale, _ = nllf_scale(self.problem)
        value = "%.15g" % (scale * history.value[0])
        out = self._pattern % dict(point=point, time=time,
                                   value=value, step=step)
        self.fid.write(out)
