
with open('ORDER_PARAMETER.xyz','r') as fp, open('ORDER_PARAMETER_AA.xyz','w') as fp_out:
    

    for l in fp.readlines():
        ls=l.split()
        if len(ls)==5:
            ls[1:4]=[str(float(i)*10) for i in ls[1:4]]
            l=' '.join(ls)+'\n'
        fp_out.write(l)
