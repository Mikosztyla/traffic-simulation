class MOBIL:
    def __init__(self, politeness, save_dcc, acc_thr, bias):
        self.politeness = politeness    # 0 - egoistic
        self.save_dcc = save_dcc
        self.acc_thr = acc_thr
        self.bias = bias

    def consider_line_change(self, curr_acc, new_acc, new_acc_other, to_right):
        # safety
        if new_acc_other < -self.save_dcc:
            return False
        
        # incentive
        to_right_factor = 1 if to_right else -1
        incentive_val = new_acc - curr_acc + self.politeness * new_acc_other + self.bias * to_right_factor

        return incentive_val > self.acc_thr
