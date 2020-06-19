
import subprocess


def exec_cmd(cmd):
    """
    Executes a bash command
    """
    ret, out, errstr = 0, None, None
    cmd = '/bin/bash -o pipefail -c \'{}\''.format(cmd)
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                      shell=True)
    except subprocess.CalledProcessError as err:
        errstr = err.output
        ret = err.returncode
    return (ret, out, errstr)


class CorpusStats:

    def __init__(self, **kwargs):
        self.corpus = kwargs['corpus']

    def disk_size(self):
        cmd = 'du -s {} | cut -f1'.format(self.corpus.root_path)
        ret, out, errstr = exec_cmd(cmd)
        if errstr:
            raise 'Error'
        return int(out)

    def get_stats(self):
        stats = {
            'disk_size': self.disk_size()
        }
        return stats


class PlainCorpusStats(CorpusStats):

    def __init__(self, **kwargs):
        self.corpus = kwargs['corpus']
        self.options = kwargs
        self.fpaths = self.corpus.get_filepaths()

        CorpusStats.__init__(self, **kwargs)

    def num_tokens(self):
        tot_tokens = 0
        for path in self.fpaths:
            cmd_tokens = 'tr " " "\n" < "{}" | wc -l | cut -f1'.format(path)
            _, num_tokens, e3 = exec_cmd(cmd_tokens)
            tot_tokens += int(num_tokens)
        return tot_tokens

    def num_lines(self):
        tot_lines = 0
        for path in self.fpaths:
            cmd_lines = 'wc -l {} | cut -d" " -f1'.format(path)
            _, num_lines, e3 = exec_cmd(cmd_lines)
            tot_lines += int(num_lines)
        return tot_lines

    def num_uniq_lines(self):
        tot_ulines = 0
        for path in self.fpaths:
            cmd_ulines = 'awk \'\\\'\'!($0 in a) {{a[$0];print}}\'\\\'\' "{}" | wc -l'\
                         '| cut -f1'.format(path)
            _, num_ulines, e3 = exec_cmd(cmd_ulines)
            tot_ulines += int(num_ulines)
        return tot_ulines

    def num_uniq_tokens(self):
        tot_utokens = 0
        for path in self.fpaths:
            cmd_utokens = 'tr " " "\n" < "{}" | awk \'\\\'\'!($0 in a)'\
                          '{{a[$0];print}}\'\\\'\' | wc -l | cut -f1'.format(path)
            _, num_utokens, e3 = exec_cmd(cmd_utokens)
            tot_utokens += int(num_utokens)
        return tot_utokens

    def get_stats(self):
        stats = CorpusStats.get_stats(self)

        more_stats = {
            'lines': self.num_lines(),
            'uniq_lines': self.num_uniq_lines(),
            'tokens': self.num_tokens(),
            'uniq_tokens': self.num_uniq_tokens()
        }
        stats.update(more_stats)
        return stats
