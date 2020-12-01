def part_1():
    with open("input.txt", "r") as input_file:
        lines = input_file.readlines()
        for i in range(len(lines)):
            for j in range(i, len(lines)):
                if int(lines[i]) + int(lines[j]) == 2020:
                    print(int(lines[i]) * int(lines[j]))


def part_2():
    with open("input.txt", "r") as input_file:
        lines = input_file.readlines()
        for i in range(len(lines)):
            for j in range(i, len(lines)):
                for k in range(j, len(lines)):
                    if int(lines[i]) + int(lines[j]) + int(lines[k]) == 2020:
                        print(int(lines[i]) * int(lines[j]) * int(lines[k]))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    part_1()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
