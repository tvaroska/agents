from time import sleep
from subprocess import Popen, PIPE

gem = Popen(['gemini', '-y'], text=True, stdin=PIPE, stdout=PIPE)
sleep(5)
gem.stdin.write('create TEST.md and write number 10 in it\n')

id = 1
for line in gem.stdout.readlines():
    print(f'{id} - {line}')
    id += 1
    

# SLEEP = 5

# run = True
# while run:
#     sleep(SLEEP)
#     content = gem.stdout.read()
#     if len(content) == 0:
#         run = False
#     else:
#         print(10 * '-')
#         print(content)