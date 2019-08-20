import os


def calc(txt):
    with open(txt, "r") as f:
        lines = f.readlines()

    ctgs = {}

    for line in lines:
        cls = os.path.basename(line)
        cls = cls.split("-")[0]
        cls = "_".join(cls.split("_")[:-1])

        if cls not in ctgs:
            ctgs[cls] = 0
        else:
            ctgs[cls] +=1

    for cls, value in ctgs.items():
        print(f"{cls} {value}")


# def clean(txt):
#     badCls = [ "Akhaltekinskiy-kon-2011",
#    "klyuch_k_serdtsu_2017",
#    "koala_s_opala_2012",
#    "koleso_fortuny_2018": 17,
#    "lastochkino_gnezdo_2012": 18,
#    "livadiyskiy_dvorets_2013": 19,
#    "london_2014": 20,
#    "lyubov_dragotsenna_2018": 21,
#    "matrona_moskvina_2017": 22
# ]
#
#     with open(txt, "r") as f:
#         lines = f.readlines()
#
#     lines = [line for line in lines if not any((cls in line for cls in badCls))]
#
#     with open(txt.replace(".txt", "_cleaned.txt"), "w") as f:
#         f.writelines(lines)

def dec(path):
    with open(path, "r") as f:
        lines = f.readlines()

    fout = open("traindetector.txt", "w")

    cnt = 0
    for line in lines:
        cls = os.path.basename(line)
        cls = "_".join(cls.split("_")[:-1])

        if cls == "belyye_nochi_2013":
            cnt += 1
            if cnt % 5:
                continue
            else:
                fout.write(line)
        else:
            fout.write(line)


def main():
    calc(r"C:\Projects\prepare_coins_data\traindetector.txt")
    # dec(r"C:\Projects\prepare_coins_data\trainD.txt")


if __name__ == "__main__":
    main()