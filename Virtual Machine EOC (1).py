memory = []
i = 0
#clears memory
while(i < (2**16)):
    memory.append("0000000000000000")
    i += 1


i = 0
Registers = []
while(i<8):
    Registers.append("0000000000000000")
    i += 1
instructionRegister = ""
instructionPTR = "0000000000000000"
N = "0"
Z = "0"
P = "0"
programCounter = 0
halt = False
addr = 0
lines = []

def bootUp():
    global instructionPTR, instructionRegister, N, Z, P, addr, lines
    g = input("Enter command: ")
    g = g.split(" ")
    
    if(g[0] == "LOAD"):
        inFile = open(g[1])
        addr = int(g[2])
        lines = inFile.readlines()
        instructionPTR = lines[addr]
        
    elif(g[0] == "DUMP"):
        i = 0
        x = int(instructionPTR)
        while(i < (2**9)):
            print(hex(x)+ ": " + memory[x])
            x += 1
        
    elif(g[0] == "REGISTERS"):
        for i in Registers:
            print(i)

    elif (g[0] == "STATE"):
        print("Memory\n")
        i = 0
        x = int(instructionPTR)
        #while(i < (2**9)):
         #   print(hex(x)+ ": " + memory[x])
          #  x += 1
        print("\nRegisters\n")
        for i in Registers:
            print(i)
        print("N = ", N)
        print("Z = ", Z)
        print("P ", P)
        print("Instruction Pointer: ", instructionPTR)
        print("Instruction Register: ", instructionRegister)
        
    elif (g[0] == "RUN"):
        programCounter = "00000000000000000"
        while(programCounter[6] == "0" and halt != True):
            instructionRegister = instructionPTR
            decode(instructionRegister)
            addr += 1
            if(addr < len(lines)):
                instructionPTR = lines[addr]
            programCounter = binAdd(programCounter, "0000000000000001")
        
def binAdd(s1,s2):
    maxlen = max(len(s1), len(s2))
    s1 = s1.strip()
    s2 = s2.strip()
    
    s1 = s1.zfill(maxlen)
    s2 = s2.zfill(maxlen)

    result  = ''
    carry   = 0

    i = maxlen - 1
    while(i >= 0):
        s = int(s1[i]) + int(s2[i])
        if s == 2: #1+1
            if carry == 0:
                carry = 1
                result = "%s%s" % (result, '0')
            else:
                result = "%s%s" % (result, '1')
        elif s == 1: # 1+0
            if carry == 1:
                result = "%s%s" % (result, '0')
            else:
                result = "%s%s" % (result, '1')
        else: # 0+0
            if carry == 1:
                result = "%s%s" % (result, '1')
                carry = 0   
            else:
                result = "%s%s" % (result, '0') 

        i = i - 1;

    if carry>0:
        result = "%s%s" % (result, '1')
    return result[::-1]

def updateNZP(binStr):
    global N, Z, P
    if(binStr[0] == "1"):
        N = 1
    else:
        positiveCount = 0
        for i in binStr:
            if(i == "1"):
                positiveCount = 1
        if(positiveCount != 0):
            P = 1
        else:
            Z = 1


    

def decimalToBinary(n):
    temp = bin(n)
    temp = temp[2:]
    binStr = ""
    while(len(binStr) + len(temp) != 16):
        binStr += "0"
    binStr = binStr + temp
    return binStr
    
##############################################################
##############################################################
##############################################################

def halt(binStr):
    global halt
    opcode = "HALT"
    halt = True
    print(opcode)

def add(binStr):
    opcode = "ADD"
    DR ="R" + str(int(binStr[4:7],2))
    SR ="R" + str(int(binStr[7:10],2))
    if binStr[10] == "1":
        imm5 = binStr[11:]
        if(imm5[0] == "0"):
            result = "00000000000"
            result += imm5
        else:
            result = "11111111111"
            result += imm5
        Registers[int(DR[1])] = binAdd(Registers[int(SR[1])],result)
        print(opcode, DR, SR, imm5)
    else:
        SR2 = "R" + str(int(binStr[13:],2))
        Registers[int(DR[1])] = binAdd(Registers[int(SR[1])], Registers[int(SR[1])])
        print(opcode, DR, SR, SR2)
    
    updateNZP(Registers[int(DR[1])])

def And(binStr):
    opcode = "AND"
    DR ="R" + str(int(binStr[4:7],2))
    SR ="R" + str(int(binStr[7:10],2))
    counter = 0
    result = ""
    extended = ""
    if(binStr[10] == "0"):
        SR2 = "R" + str(int(binStr[13:]))
        value = Registers[int(SR2[1])]
        
        for i in Registers[int(SR[1])]:
            if (i == value[counter]):
                result += "1"
            else:
                result += "0"
            counter += 1
        print(opcode, DR, SR, SR2)
        Registers[int(DR[1])] = result
    else:
        imm5 = binStr[11:]
        if(imm5[0] == "0"):
            extended = "00000000000"
            extended += imm5
        else:
            extended = "11111111111"
            extended += imm5
        for i in SR:
            if (i == extended[counter]):
                result += "1"
            else:
                result += "0"
            counter += 1
        print(opcode, DR, SR, extended)
        Registers[int(DR[1])] = result
        
    updateNZP(Registers[int(DR[1])])

def Not(binStr):
    opcode = "NOT"
    DR ="R" + str(int(binStr[4:7],2))
    SR ="R" + str(int(binStr[7:10],2))
    complement = ""
    
    for i in Registers[int(SR[1])]:
        if(i == "0"):
            complement += "1"
        else:
            complement += "0"

    Registers[int(DR[1])] = complement
    updateNZP(Registers[int(DR[1])])
    print(opcode, DR, SR)

def LD(binStr):
    global instructionPTR
    opcode = "LD"
    DR ="R" + str(int(binStr[4:7],2))
    address = binStr[7:16]
    address = address + instructionPTR[10:]
    Registers[int(DR[1])] = memory[int(address,2)]

    updateNZP(Registers[int(DR[1])])
    print(opcode, DR)
    
def LDI(binStr):
    global instructionPTR
    opcode = "LDI"
    DR ="R" + str(int(binStr[4:7],2))
    address = binStr[7:]
    address = address.strip()
    address = address + instructionPTR[10:]
    pointer = memory[int(address,2)]
    Registers[int(DR[1])] = memory[int(pointer,2)]
    
    updateNZP(Registers[int(DR[1])])
    print(opcode, DR)
    
def ST(binStr):
    global instructionPTR
    opcode = "ST"
    SR ="R" + str(int(binStr[4:7],2))
    address = binStr[7:]
    address = address + instructionPTR[10:]
    memory[int(address,2)] = Registers[int(SR[1])]
    print(opcode, SR)
    
def STI(binStr):
    global instructionPTR
    opcode = "STI"
    SR ="R" + str(int(binStr[4:7],2))
    address = binStr[7:]
    address = address + instructionPTR[11:]
    pointer = memory[int(address,2)]
    memory[int(pointer,2)] = Registers[int(SR[1])]

    print(opcode, SR)
    
def GET(binStr):
    opcode = "GET"
    DR = "R" + str(int(binStr[4:7],2))
    command = input("Enter your input: ")
    if(binStr[5] == "0"):
        command = int(command,2)
        Registers[int(DR[1])] = decimalToBinary(command)
    else:
        Registers[int(DR[1])] = command

    print(opcode, DR)
    updateNZP(Registers[int(DR[1])])
    
def PUT(binStr):
    opcode = "PUT"
    SR = "R" + str(int(binStr[4:7],2))
    value = Registers[int(SR[1])]
    if(binStr[7] == "0"):
        print(int(value,2))
    else:
        print(value)
        
def BR(binStr):
    opcode = "BR"
    global instructionPTR, N, Z, P
    n = binStr[4]
    z = binStr[5]
    p = binStr[6]
    adjust = False
    
    if(n == "1" and N == "1"):
        adjust = True
    elif(z == "1" and Z == "1"):
        adjust = True
    elif(p == "1" and P == "1"):
        adjust = True
    if(adjust == True):
        offset = binStr[7:]
        instructionPTR = offset + instructionPTR[11:]
    
def JMP(binStr):
    global instructionPTR
    opcode = "JMP"
    L = binStr[4]
    offset = binStr[7:]
    if(L == "0"):
        instructionPTR = offset + instructionPTR[11:]
    else:
        Registers[7] = instructionPTR
        instructionPTR = offset + instructionPTR[11:]        
    print(opcode)

    
def RET(binStr):
    global halt
    opcode = "RET"
    global insructionPTR
    instructionPTR = Registers[7]
    print(opcode, instructionPTR)
    halt = True
    

instrDict = {"0000":halt, "0001":add, "0010":And, "0011":Not, "0100":LD,
             "0101":LDI,"0111":ST, "1000":STI, "1010":GET, "1011":PUT, "1100":BR,"1101":JMP, "1111":RET}


def decode(binStr):

    opcode = binStr[0:4]
    instrDict[opcode](binStr)
