from colorama import Fore

from CmdInterpreter import CmdInterpreter

"""
    AUTHORS' SCOPE:
        We thought that the source code of Jarvis would
        be more organized if we treat Jarvis as Object.
        So we decided to create this Jarvis Class which
        implements the core functionality of Jarvis in a
        simpler way than the original __main__.py.
    HOW TO EXTEND JARVIS:
        In progress..
    DETECTED ISSUES:
        * Furthermore, "near me" command is unable to find
        the actual location of our laptops.
"""


class Jarvis(CmdInterpreter):
    # We use this variable at Breakpoint #1.
    # We use this in order to allow Jarvis say "Hi", only at the first
    # interaction.
    first_reaction_text = ""
    first_reaction_text += Fore.BLUE + 'BOT sound is by default disabled.' + Fore.RESET
    first_reaction_text += "\n"
    first_reaction_text += Fore.BLUE + 'In order to let BOT talk out loud type: '
    first_reaction_text += Fore.RESET + Fore.RED + 'enable sound' + Fore.RESET
    first_reaction_text += "\n"
    prompt = Fore.RED + "~> Hi, what can i do for you?\n" + Fore.RESET

    # This can be used to store user specific data

    def __init__(self, first_reaction_text=first_reaction_text,
                 prompt=prompt, first_reaction=True, enable_voice=False):
        CmdInterpreter.__init__(self, first_reaction_text, prompt,
                                first_reaction, enable_voice)

    def default(self, data):
        """BOT let's you know if an error has occurred."""
        if self.enable_voice:
            self.speech.text_to_speech("I could not identify your command")
        print(Fore.RED + "I could not identify your command..." + Fore.RESET)

    def precmd(self, line):
        """Hook that executes before every command."""
        words = line.split()
        if len(words) == 0:
            line = "None"
        elif len(words) == 1:
            pass
        elif (len(words) > 2) or (words[0] not in self.actions):
            line = self.parse_input(line)
        return line

    def postcmd(self, stop, line):
        """Hook that executes after every command."""
        if self.first_reaction:
            self.prompt = self.prompt = Fore.RED + "~> What can i do for you?\n" + Fore.RESET
            self.first_reaction = False
        if self.enable_voice:
            self.speech.text_to_speech("What can i do for you?\n")

    def speak(self):
        if self.enable_voice:
            self.speech.speak(self.first_reaction)

    def parse_input(self, data):
        """This method gets the data and assigns it to an action"""
        output = "None"

        data = data.lower()

        # say command is better if data has punctuation marks
        if "say" not in data:
            data = data.replace("?", "")
            data = data.replace("!", "")
            data = data.replace(".", "")
            data = data.replace(",", "")

        # Check if Jarvis has a fixed response to this data
        if data in self.fixed_responses:
            output = self.fixed_responses[data]  # change return to output =
        else:
            # if it doesn't have a fixed response, look if the data corresponds to an action
            output = self._find_action(data)

        return output

    def _find_action(self, data):
        """Checks if input is a defined action.
        :return: returns the action"""
        output = "None"
        action_found = False

        words = data.split()
        words_remaining = data.split()  # this will help us to stop the iteration

        # check word by word if exists an action with the same name
        for word in words:
            words_remaining.remove(word)
            for action in self.actions:
                # action can be a string or a dict
                if type(action) is dict and word in action.keys():
                    # command name exists, assign it to the output
                    action_found = True
                    output = self._generate_output_if_dict(action, word, words_remaining)
                    break
                elif word == action:  # command name exists
                    action_found = True
                    output = word + " " + " ".join(words_remaining)
                    break
            if action_found:
                break
        return output

    @staticmethod
    def _generate_output_if_dict(action, word, words_remaining):
        """Generates the correct output if action is a dict"""
        output = word

        # command is a dictionary, let's check if remaining words are one of it's completions
        if len(words_remaining) != 0:
            command_arguments = list(words_remaining)  # make a copy
            for argument in words_remaining:
                command_arguments.remove(argument)
                for value in action[word]:
                    if argument == value:
                        output += " " + argument
                        output += " " + " ".join(command_arguments)
        return output

    def executor(self):
        """
        This method is opening a terminal session with the user.
        We can say that it is the core function of this whole class
        and it joins all the function above to work together like a
        clockwork. (Terminates when the user send the "exit", "quit"
        or "goodbye command")
        :return: Nothing to return.
        """
        self.speak()
        self.cmdloop(self.first_reaction_text)

