class SimpleCommand:
    commands = {}
    def __init__(self, key, inputHandle,  help=None, confirm = False):
        self.inputHandle = inputHandle 
        self.help = help
        self.commands[key] = self

            
    def __call__(self, session, input):
        if not input:
            return self.help if not self.help is callable or self.help(session)
        
        return self.inputHandle(session, input)
