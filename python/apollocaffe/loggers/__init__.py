from time import strftime
import apollocaffe
import numpy as np
import os

class TrainLogger(object):
    def __init__(self, display_interval, log_file="/tmp/apollocaffe_log.txt"):
        self.display_interval = display_interval
        self.log_file = log_file
        os.system("touch %s" % self.log_file)
    def log(self, idx, meta_data):
        meta_data['start_iter'] = meta_data.get('start_iter', 0)
        if idx == meta_data['start_iter']:
            #TODO: move to separate DeviceLogger
            current_device = apollocaffe.CppConfig.get_device()
            if current_device == -1:
                device_info = "CPU device"
            else:
                device_info = "GPU device %d" % current_device
            log_line = ""
            try:
                log_line = "%s - Training on %s" % \
                    (strftime("%Y-%m-%d %H:%M:%S"), device_info)
            except:
                log_line = "Skipping training log: Unknown Error"

            try:
                with open(self.log_file, 'ab+') as lfile:
                    lfile.write("%s\n" % log_line)
            except IOError:
                print "Trainer Logger Error: %s does not exist." % self.log_file
            except Exception as e:
                print e
            print log_line

        if idx % self.display_interval == 0:
            log_line = ""
            try:
                loss = np.mean(meta_data['train_loss'][-self.display_interval:])
                log_line = "%s - Iteration %4d - Train Loss: %g" % \
                    (strftime("%Y-%m-%d %H:%M:%S"), idx, loss)
            except Exception as ex:
                log_line += str(ex)
                log_line = "Skipping training log: Unknown Error"

            try:
                with open(self.log_file, 'ab+') as lfile:
                    lfile.write("%s\n" % log_line)
            except IOError:
                print "Trainer Logger Error: %s does not exist." % self.log_file
            except Exception as e:
                print e
            print log_line

class ValLogger(object):
    def __init__(self, display_interval, log_file="/tmp/apollocaffe_log.txt"):
        self.display_interval = display_interval
        self.log_file = log_file
        os.system("touch %s" % self.log_file)
    def log(self, idx, meta_data):
        if idx % self.display_interval == 0:
            try:
                log_line = "%s - Iteration %4d - Validation Loss: %g" % \
                    (strftime("%Y-%m-%d %H:%M:%S"), idx, meta_data['val_loss'][-1])
            except IndexError:
                log_line = "Skipping validation log: \
You have not provided a Validation Set"
            else:
                log_line =  "Skipping validation log: Unknown Error"

            try:
                with open(self.log_file, 'ab+') as lfile:
                    lfile.write("%s\n" % log_line)
            except IOError:
                print "Validation Logger Error: %s does not exist." % self.log_file
            except Exception as e:
                print e
            print log_line

class SnapshotLogger(object):
    def __init__(self, snapshot_interval, snapshot_prefix='/tmp/model',
            log_file="/tmp/apollocaffe_log.txt"):
        self.snapshot_interval = snapshot_interval
        self.snapshot_prefix = snapshot_prefix
        self.log_file = log_file
        os.system("touch %s" % self.log_file)
    def log(self, idx, meta_data):
        meta_data['start_iter'] = meta_data.get('start_iter', 0)
        if idx % self.snapshot_interval == 0 and idx > meta_data['start_iter']:
            try:
                filename = '%s_%d.h5' % (self.snapshot_prefix, idx)
                log_line = "%s - Iteration %4d - Saving net to %s" % \
                    (strftime("%Y-%m-%d %H:%M:%S"), idx, filename)
                print(log_line)
                meta_data['apollo_net'].save(filename)
            except Exception as e:
                print e
                print('Saving failed')