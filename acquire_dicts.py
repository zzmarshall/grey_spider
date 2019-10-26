import os
import pickle
from conf.base_config import Config

dict_path = "{}/dicts".format(Config["bin_path"])


def init_dict(name):
    filename = "{}/{}.pickle".format(dict_path, name)
    if not os.path.exists(filename):
        return {}
    return pickle.load(open(filename, "r"))

def dump_dict(data, name):
    pickle.dump(data, open("{}/{}.pickle".format(dict_path, name) , "w"))
    with open("{}/{}.txt".format(dict_path, name), "w") as fp:
        for k, v in data.items():
            fp.write("{}\t{}\n".format(k, v))


if __name__ == "__main__":
    print init_dict("zone")
