import inspect
from time import sleep

from requests import Session
from requests.utils import cookiejar_from_dict
from os.path import isdir, exists, join, dirname, realpath
from os import mkdir, getcwd
from bs4 import BeautifulSoup
from re import search as regex_search


class AocInteraction:
    def __init__(self):
        self.__location__ = realpath(join(getcwd(), dirname(__file__)))
        if not exists(join(self.__location__, '.session')):
            open(join(self.__location__, '.session'), 'w').close()
        with open(join(self.__location__, '.session'), 'r') as f:
            session_token = f.readline()
            if session_token:
                self.year = 2020
                self.hints = True

                self.session = Session()
                self.session.cookies = cookiejar_from_dict({'session': session_token})
            else:
                print("Insert your session token in `.session` You can find the token in a cookie on adventofcode.com; it is valid for a month after logging in.")
                exit(1)

    def pull(self, wait=True):
        for day in range(1, 26):
            main_response = self.session.get('https://adventofcode.com/' + str(self.year) + '/day/' + str(day))
            day_name = "Day " + str(day)
            if main_response.status_code == 200:
                if not isdir(join(self.__location__, day_name)):
                    print(day_name)
                    mkdir(day_name)
                if not exists(join(self.__location__, day_name, "input.txt")):
                    print(day_name, "-", "input.txt")
                    input_response = self.session.get('https://adventofcode.com/' + str(self.year) + '/day/' + str(day) + "/input")
                    if input_response.status_code == 200:
                        with open(join(self.__location__, day_name, "input.txt"), "w") as f:
                            f.write(str(input_response.text))
                            f.close()

                if not exists(join(self.__location__, day_name, "main.py")):
                    f = open(join(self.__location__, day_name, "main.py"), "w+")
                    f.close()
                with open(join(self.__location__, day_name, "main.py"), 'r+') as f:
                    old = f.read()
                    soup = BeautifulSoup(main_response.content, features='html.parser')
                    parts = soup.findAll("article")
                    if old == "":
                        print(day_name, "-", "Main.py")
                        f.write("from pull import AocInteraction\n\n\n#  https://adventofcode.com/" + str(self.year) + "/day/" + str(day) + "\n")
                        lines = [i for i in parts[0].get_text().replace(" ---", " ---\n").split("\n") if i]
                        f.write(str('\n'.join(map(lambda x: "#  " + x, lines))))
                        f.write("""
def part_1(advent_of_code):
    with open('input.txt', 'r') as input_file:
        
        advent_of_code.answer(1, None)
\n
def part_2(advent_of_code):
    with open('input.txt', 'r') as input_file:
        
        advent_of_code.answer(2, None)
\n
if __name__ == "__main__":
    aoc_interaction = AocInteraction()
    part_1(aoc_interaction)
    part_2(aoc_interaction)
""")
                    if len(parts) == 2:
                        f.seek(0)
                        old = f.read()
                        old_split = old.split("\n")
                        for line_nr in range(len(old_split)):
                            if old_split[line_nr] == 'def part_2(advent_of_code):' and (old_split[line_nr - 1] == "" or old_split[line_nr - 1][0] != "#"):
                                prefix = ""
                                if old_split[line_nr - 1] != "":
                                    prefix = "\n\n"
                                print("Found!")
                                lines = [i for i in parts[1].get_text().replace(" ---", " ---\n").split("\n") if i]
                                old_split.insert(line_nr, prefix + (str('\n'.join(map(lambda x: "#  " + x, lines)))))
                                break
                        f.seek(0)
                        f.write("\n".join(old_split))
            elif main_response.text.startswith("Please don't repeatedly request this endpoint before it unlocks!"):
                countdown_page = self.session.get('https://adventofcode.com/' + str(self.year))
                countdown_f = regex_search("var server_eta = (\d+);", countdown_page.text)
                if wait and countdown_f and countdown_f.group(1):
                    countdown_s = countdown_f.group(1)
                    print(day_name, "This day is not yet unlocked... It will take about", self._s_to_text(countdown_s), "seconds to unlock.")
                    print("Waiting to unlock automatically... To cancel, terminate script.")
                    sleep(int(countdown_s))
                    print("Unlocking...")
                    self.pull()
                break
            else:
                print(day_name, "-", "Error found:", str(main_response.status_code), main_response.text)
                break

    def answer(self, part, a):
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        x = regex_search("Day (\d+)", dirname(mod.__file__))
        if not x or not x.group(1):
            frm = inspect.stack()[2]
            mod = inspect.getmodule(frm[0])
            x = regex_search("Day (\d+)", dirname(mod.__file__))
            if not x or not x.group(1):
                print("Cannot find day")
                return
        day = x.group(1)
        prefix = "Day " + str(day) + " - Part " + str(part) + " ||"

        if a is None:
            print(prefix, "Not answered; answer is None")
        else:
            if not exists(join(self.__location__, "Day " + str(day), ".answers_" + str(part))):
                f = open(join(self.__location__, "Day " + str(day), ".answers_" + str(part)), "w+")
                f.close()
            with open(join(self.__location__, "Day " + str(day), ".answers_" + str(part)), "r+") as previous_answers:
                old = previous_answers.read()
                old_split = old.split("\n")

                temp = old_split
                temp.reverse()
                found = False

                if self.hints:
                    low_border = None
                    high_border = None

                    # low_border = max([int(line.split("    ")[0]) for line in temp if len(line.split("    ")) == 2 and line.split("    ")[1].endswith("<<<too low>>>")])
                    # high_border = min([int(line.split("    ")[0]) for line in temp if len(line.split("    ")) == 2 and line.split("    ")[1].endswith("<<<too high>>>")])
                    for line in temp:
                        split_line = [x for x in line.split('    ', 1) if x]
                        if len(split_line) == 2 and split_line[1].endswith("<<<too low>>>") and (low_border is None or int(split_line[0]) > low_border):
                            low_border = int(split_line[0])
                        elif len(split_line) == 2 and split_line[1].endswith("<<<too high>>>") and (high_border is None or int(split_line[0]) < high_border):
                            high_border = int(split_line[0])
                    if low_border is not None and low_border > int(a):
                        print(prefix, "Your answer is likely to be wrong; you have provided", a, "while you have previously provided", str(low_border) + ", which was too low.")
                        return
                    elif high_border is not None and high_border < int(a):
                        print(prefix, "Your answer is likely to be wrong; you have provided", a, "while you have previously provided", str(high_border) + ", which was too high.")
                        return

                for line in temp:
                    split_line = [x for x in line.split('    ', 1) if x]
                    if len(split_line) == 2 and split_line[1].endswith("<<<CORRECT>>>"):
                        print(prefix, "You have already correctly answered this question. The answer was", split_line[0] + ". Your current answer is " + str(a))
                        found = True
                        break
                    elif len(split_line) == 1 and split_line[0] == str(a):
                        if len(split_line) == 2 and self.hints:
                            print(prefix, "You answered", a, "---", "You have already provided that answer. That answer was", regex_search("<<<([\w\s]+)>>>", split_line[1]).group(1) + ".")
                        else:
                            print(prefix, "You answered", a, "---", "You have already provided that answer.")
                        found = True
                        break
                if not found:
                    print(prefix, "Answering: ", a)
                    response = self.session.post('https://adventofcode.com/' + str(self.year) + '/day/' + str(day) + "/answer", {'level': part, 'answer': str(a)})
                    if response.status_code == 200:
                        response = BeautifulSoup(response.content, features='html.parser').find("article")
                        t = response.get_text()
                        if t.startswith("You gave an answer too recently;"):
                            seconds_find = regex_search("You have ((\d+)m\s*)?(\d+)s left to wait.", t)
                            if seconds_find:
                                s = int(seconds_find.group(3)) + 1
                                if seconds_find.group(2):
                                    s += 60 * int(seconds_find.group(2))
                                print(prefix, "Too fast! Waiting for", s, "seconds before automatic retry!")
                                sleep(s)
                                self.answer(part, a)
                        elif t.startswith("That's not the right answer"):
                            print(prefix, t)
                            if t.startswith("That's not the right answer; your answer is too high."):
                                old_split.append(str(a) + "    <<<too high>>>")
                            elif t.startswith("That's not the right answer; your answer is too low."):
                                old_split.append(str(a) + "    <<<too low>>>")
                            else:
                                old_split.append(str(a))
                            previous_answers.seek(0)
                            previous_answers.write("\n".join([x for x in old_split if x]))
                        elif t.startswith("That's the right answer!"):
                            print(prefix, t)
                            old_split.append(str(a) + "    <<<CORRECT>>>")
                            previous_answers.seek(0)
                            previous_answers.write("\n".join([x for x in old_split if x]))
                            self.pull(wait=False)
                        elif t.startswith("You don't seem to be solving the right level."):
                            print(prefix, t)
                        elif t.startswith("--- Day"):
                            print(prefix, "There is likely something wrong with your session token, maybe it is outdated. Please fix it in `.session` before continuing.")
                        else:
                            print(t)
                    elif response.status_code == 302:
                        print(prefix, "Fill in your session token in `.session`.")
                    else:
                        print(prefix, "Error found:", response.status_code, response.text)
        return

    @staticmethod
    def _s_to_text(s):
        s = int(s)
        t = ""
        if s > 3600:
            t += str(int(s / 3600)) + "h "
        s = s % 3600
        if s > 60:
            t += str(int(s / 60)) + "m "
        s = s % 60
        if s > 0:
            t += str(s) + "s "
        return t.strip()


if __name__ == "__main__":
    interact = AocInteraction()
    interact.pull()
