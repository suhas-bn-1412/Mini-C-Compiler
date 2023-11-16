import re
import math

"""
# R0-12 must be used
# R0-2 should be used to get the address from variables of C program
# rest other registers should be used for the other purpose
# reading the address of C variable should be done twice, once while load and other while store 
emptyaddreg=[0,1,2]
busyaddreg=[]
emptyreg=[3,4,5,6,7,8,9,10,11,12]
busyreg=[]
"""

free_reg=[0,1,2,3,4,5,6,7,8,9,10,11,12]
busy_reg=[]
mappings = {}
stored = []

def get_var_map(reg): #gives which variable/temp is assigned to register reg
    global mappings
    if(mappings["reg"] == ""):
        return "none"
    return mappings["reg"]
    
def get_reg_map(var): #gives which register is holding the value of the variable
    global mappings
    for key, value in mappings.items():
        if(value == var):
            return key
    return "none"

#allots reg for the variable and updates the mappings
def allot_reg(var):
    global mappings
    global free_reg
    global busy_reg
    #if reg is already aloted return that
    if(var in mappings.values()):
        reg_alloted = get_reg_map(var)
        return reg_alloted
    #else allot new one , update the mappings and return the new one
    else:
        free = min(free_reg) #reg which is currently free
        free_reg.remove(free) #remove that from current free list
        busy_reg.append(free) #put it into busy list
        mappings[free] = var
        return free

def det_const_var_temp(word):
    if(len(re.findall("^t[0-9]+$",word))!=0): #then its a temp
        return "temp"
    elif(len(re.findall("^\*",word))!=0): #then its a ptr
        return "ptr"
    elif(len(re.findall("^[0-9]+$",word))!=0): #then its a const
        return "const"
    elif(len(re.findall("^[a-zA-Z]([a-zA-Z]|[0-9])*$", word))!=0):
        return "var"
    return "memacc" #may be mem access - t2 = a[t1] / t2 = *p

###########################
#   LOAD STORE MOVE     #
def det_mov_ld_st(words):
    dest = det_const_var_temp(words[0])
    src = det_const_var_temp(words[2])
    #print("dest:",dest)
    #print("src:",src)
    #var and constant - move, a = 0 -> mov r1, #0
    #var and temp - store,  a = t1 -> st a,r1 (r1 has t1)
    if(src == "ptr"): #t1 = *p -> ld r1,p and mov r2, 0(r1)
        return "ld_mov"
    if(dest == "var"):
        if(src == "const"):
            return "move"
        else:
            return "store"
    #temp and var - load, t1 = a -> ld r1,a
    #temp and memacc - move, t2 = a[t1] -> mov r2, r1(a) (r1 has t1)
    #temp and temp - move , t2 = t1 -> mov r2,r1
    else:
        if(src == "var"):
            return "load"
        else:
            return "move"

#function to generate load followed by move
def gen_ld_mov(words):
    #i/p -> t2 = *p
    #o/p -> ld r1, p and mov r2, 0(r1)
    #mappings -> r1-p, r2-t2

    #get a reg for p and t2, update mapping there itself
    temp = words[0]
    var = words[2][1:]
    reg1 = allot_reg(temp)
    reg2 = allot_reg(var)

    #ld reg1, var
    load = "LD R{}, {}".format(reg1, var)
    #mov reg2, 0(reg1)
    move = "MOV R{}, 0(R{})".format(reg2, reg1)

    #return or print
    print(load)
    print(move)

#function which forms move statement
def gen_mov_stmt(words): 
    #var and const a=0 -> mov reg, const and map var,reg
    if(det_const_var_temp(words[0]) == "var"):
        var = words[0]
        const = words[2]
        reg = allot_reg(var)
        move = "MOV R{}, #{}".format(reg,const)

    else:
        #temp and temp t2 = t1 -> mov reg2, reg1
        if(det_const_var_temp(words[2]) == "temp"):
            temp2 = words[0]
            temp1 = words[2]
            reg2 = allot_reg(temp2)
            reg1 = allot_reg(temp1)
            move = "MOV R{}, R{}".format(reg2,reg1)

        #temp and const t1 = 20
        elif(det_const_var_temp(words[2]) == "const"):
            temp = words[0]
            const = words[2]
            reg = allot_reg(temp)
            move = "MOV R{}, #{}".format(reg,const)

        #temp and memacc t2 = a[t1] -> mov r2, r1(a)
        else:
            print(words)
            temp2 = words[0]
            second_split = words[2].split("[")
            var = second_split[0]
            temp1 = second_split[1][0:-1]

            reg2 = allot_reg(temp2)
            reg1 = allot_reg(temp1)
            move = "MOV R{}, R{}({})".format(reg2, reg1, var)

    #return or print move
    print(move)

#function which forms store statement
def gen_st_stmt(words):
    #var and temp
    #i/p a=t1
    #o/p st a,r1
    #mappings r1-t1 (already present)

    var = words[0]
    temp = words[2]
    reg = get_reg_map(temp)

    store = "ST {}, R{}".format(var,reg)
    global stored
    stored.append(var)
    #return or print
    print(store)

#function which forms load statement
def gen_ld_stmt(words):
    #temp and var
    #i/p t1 = a
    #o/p  ld r1, a
    #add mapping r1-t1

    temp = words[0]
    var = words[2]
    reg = allot_reg(temp) #mapping added here only

    load = "LD R{}, {}".format(reg, var)
    print(load)

###############################



###############################
#   ADD SUB MUL DIV     #

def gen_add(words):
    #temp/var = temp/var + temp/var/imm
    dest = words[0]
    src1 = words[2]
    src2 = words[4]

    dest_reg = allot_reg(dest)
    src1_reg = allot_reg(src1)
    if(det_const_var_temp(src2) != "const"):
        src2_reg = allot_reg(src2)
    #for both temp and var get the reg
    if(det_const_var_temp(src2) == "const"):
        add = "ADD R{}, R{}, #{}".format(dest_reg, src1_reg, src2)
    else:
        add = "ADD R{}, R{}, R{}".format(dest_reg, src1_reg, src2_reg)

    print(add)

def gen_sub(words):
    #temp/var = temp/var + temp/var/imm
    dest = words[0]
    src1 = words[2]
    src2 = words[4]

    dest_reg = allot_reg(dest)
    src1_reg = allot_reg(src1)
    if(det_const_var_temp(src2) != "const"):
        src2_reg = allot_reg(src2)
    #for both temp and var get the reg
    if(det_const_var_temp(src2) == "const"):
        sub = "SUB R{}, R{}, #{}".format(dest_reg, src1_reg, src2)
    else:
        sub = "SUB R{}, R{}, R{}".format(dest_reg, src1_reg, src2_reg)

    print(sub)

def gen_mul(words):
    #temp/var = temp/var + temp/var/imm
    dest = words[0]
    src1 = words[2]
    src2 = words[4]

    dest_reg = allot_reg(dest)
    src1_reg = allot_reg(src1)
    if(det_const_var_temp(src2) != "const"):
        src2_reg = allot_reg(src2)
    #for both temp and var get the reg
    if(det_const_var_temp(src2) == "const"):
        mul = "MUL R{}, R{}, #{}".format(dest_reg, src1_reg, src2)
    else:
        mul = "MUL R{}, R{}, R{}".format(dest_reg, src1_reg, src2_reg)

    print(mul)

def gen_div(words):
    #temp/var = temp/var + temp/var/imm
    dest = words[0]
    src1 = words[2]
    src2 = words[4]

    dest_reg = allot_reg(dest)
    src1_reg = allot_reg(src1)
    if(det_const_var_temp(src2) != "const"):
        src2_reg = allot_reg(src2)
    #for both temp and var get the reg
    if(det_const_var_temp(src2) == "const"):
        div = "DIV R{}, R{}, #{}".format(dest_reg, src1_reg, src2)
    else:
        div = "DIV R{}, R{}, R{}".format(dest_reg, src1_reg, src2_reg)

    print(div)
###############################
def comparision(words):
    first = 'CMP '
    x = allot_reg(words[2])
    y = allot_reg(words[4])
    first+="{}, {}".format(x,y)
    print(first)
        
    secondvar=''
    if st[3]=='>':
        secondvar = 'BLT '
    if st[3]=="<":        
        secondvar = 'BGT '
    if st[3]=='>=':
        secondvar = 'BLE '
    if st[3]=='<=':
        secondvar = 'BGE '
    if st[3]=='==':
        secondvar = 'BNE '
    if st[3]=='!=':
        secondvar = 'BEQ '
    return secondvar
#store back everything there is in mappings
def store_mappings():
    global mappings
    for key,value in mappings.items():
        if(value not in stored):
            if(det_const_var_temp(value) == "var"):
                store = "ST {}, R{}".format(value,key)
                print(store)
                print()


if __name__ == "__main__":
    f=open("icg.txt","r")
    icg=f.readlines(1200)
    #print(icg)
    #print(type(icg))
    i = -1
    res = ''
    #print(icg[0])
    for line in icg:
        i+=1
        #print("enter")
        words = line.split(" ")
        words[-1] = words[-1].strip()

        if(len(words)==1):
            print(words[0])
            print()

        elif(len(words)==2):
            if(words[0] == 'goto'):
                res = "B {}".format(words[1])
            else:
                res = "{}{}".format(words[0],words[1])
            print(res)
            print()

        #t0 = t1 + t2
        #words = ['t0','=','t1','+','t2']
        #print("split:",words)
        elif(len(words)==3):  #load store or move
            #print("if")
            
            cond = det_mov_ld_st(words)

            if(cond == "move"):
                out = gen_mov_stmt(words)
            elif(cond == "store"):
                out = gen_st_stmt(words)
            elif(cond == "load"):
                out = gen_ld_stmt(words)
            elif(cond == "ld_mov"):
                out = gen_ld_mov(words)
            else:
                print("advanced")
                #advanced()  ##################temporary
            #store_mappings()
            print()

        elif(len(words)==5):  #computation or comparision

            cond = words[3]

            operator = ['+', '-', '*', '/']
            cmpop = ['>', '<', '>=', '<=','==','!='] 

            if(cond in operator):
                if(cond == '+'):
                    out = gen_add(words)
                elif(cond == '-'):
                    out = gen_sub(words)
                elif(cond == '*'):
                    out = gen_mul(words)
                elif(cond == '/'):
                    out = gen_div(words)

            elif(cond in cmpop):
                res = 1#comparision(words)
                next_line = icg[i+1].split(" ")
                res += next_line[3]
                print(res)
            print()

    store_mappings()
        #print(mappings)