
j = 2.0
for i in range(100):
    j*=i+1

j/=32323
print j
print "dfdfdfdfgdfdfdfgdf"



from javax.swing import JButton, JFrame

frame = JFrame('Hello, Jython!',
            defaultCloseOperation = JFrame.EXIT_ON_CLOSE,
            size = (300, 300)
        )

def change_text(event):
    print 'Clicked!'

button = JButton('Click Me!', actionPerformed=change_text)
frame.add(button)
frame.visible = True
