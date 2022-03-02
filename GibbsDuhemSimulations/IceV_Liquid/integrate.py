import numpy as np
from scipy import integrate
import  os, glob
import argparse
import numpy as np
parser = argparse.ArgumentParser(description='Set settings for Gibbs-Duhem integration.')

parser.add_argument('--initial_point_folder', type=str,
                    help='Folder containing initial point used for Gibbs-Duhem', default='Clausius')
 
parser.add_argument('--integration_variable', type=str,
                    help='Specify whether T or P is used as dependent variable.', default='P')

parser.add_argument('--end_variable', type=float,
                    help='Where to stop intergration.', default=3000.0)

parser.add_argument('--steps_per_sim', type=int,
                    help='Number of steps per simulation.', default=10000)
parser.add_argument('--left', type=str,
                    help='Left side phase.', default='IceIh')
parser.add_argument('--right', type=str,
                    help='Right side phase.', default='Liquid')

parser.add_argument('--percent_equilibration', type=float,
                    help='Percent of simulation dedicated to equilibration.', default=25.0)

parser.add_argument('--root_fold', type=str,
                    help='Folder used to store all simulations.', default='Gibbs_Duhem_Simulations/')

parser.add_argument('--step', type=float,
                    help='Step length used for integration.', default=100)

parser.add_argument('--initial_equilibration_steps', type=int,
                    help='Perform an initial simulation to equilibrate to desired pressure and temperature.', default=0)
parser.add_argument('--initial_TP', type=float,nargs=2,
                    help='Initial values for melting point T and P', default=[None,None])

parser.add_argument('--lmp_exe', type=str,
                    help='Path to lammps executable.', default='/home/sbore/software/mbx_lammps_plumed/lammps/src/lmp_mpi_mbx') 

parser.add_argument('--run_cmd', type=str,
                    help='Command for running lammps', default='srun -n 2 ')

parser.add_argument('--restart_if_possible', type=bool,
                    help='Use previous simulation if exists', default=True)
args = parser.parse_args()
args.root_fold+='/'
args.left='/'+args.left+'/'
args.right='/'+args.right+'/'
print(args)
I=0
dt=0

def rungekutta4(f, y0, t, args=()):
    n = len(t)
    y = np.zeros((n, len(y0)))
    y[0] = y0
    for i in range(n - 1):
        h = t[i+1] - t[i]
        k1 = f(y[i], t[i], *args)
        k2 = f(y[i] + k1 * h / 2., t[i] + h / 2., *args)
        k3 = f(y[i] + k2 * h / 2., t[i] + h / 2., *args)
        k4 = f(y[i] + k3 * h, t[i] + h, *args)
        y[i+1] = y[i] + (h / 6.) * (k1 + 2*k2 + 2*k3 + k4)
    f(y[-1], t[-1], *args)
    return y




def extract_form_log(fn):
    lines=open(fn,'r').readlines()
    start=np.where([('Step' in l) for l in lines])[-1][0]
    data={keyi.lower(): []  for keyi in lines[start].split()}
    for l in lines[start+1:]:
        ls=l.split()
        if ls[0].isdigit():
            for i, key in enumerate(data.keys()):
                try:
                    data[key].append(float(ls[i]))
                except:
                    pass
        else:
            break
    for key in data.keys():
        data[key]=np.array(data[key])
    return data

def fn(y,x):
    global I
    global args
    global dt
    if args.integration_variable=='P':
        P_str='{:.1f}'.format(x)
        T_str='{:.2f}'.format(y[-1])    
    elif args.integration_variable=='T':
        P_str='{:.1f}'.format(y[-1])
        T_str='{:.2f}'.format(x)     
    else:
        exit
    
    name_sim=args.root_fold+str(I)+'_'+T_str+'_'+P_str
        
    # Create directory for Gibbs-Duhem simulations
    # if simulations does not already exist
    if not os.path.isdir(name_sim) and args.restart_if_possible:
        os.system('mkdir -p {}'.format(name_sim))
    
 
        # Replace starting configuration by previous


        if abs(I)>0:
            closest=glob.glob(args.root_fold+str(int(I-np.sign(dt)))+'_*_*/')[0]
        else:
            closest=args.initial_point_folder

        os.system('cp -r  {}/{} {}/'.format(closest,args.left,name_sim))
        os.system('cp -r  {}/{} {}/'.format(closest,args.right,name_sim))



        # Specify pressure and tempreature
        cmd=''
        cmd+='sed -i  "s#variable .* pressure .*#variable        pressure equal {}#g" {}/in.pressure\n'.format(P_str,name_sim+args.right)
        cmd+='sed -i  \"s#variable.*temperature.*#variable        temperature equal {}#g\" {}/in.temp\n'.format(T_str,name_sim+args.right)
        cmd+='sed -i  \"s#thermo_style.*#thermo_style    custom step temp pe etotal epair emol press lx ly lz vol pxx pyy pzz pxy pxz pyz enthalpy#g\" {}/in.setup\n'.format(name_sim+args.right)

        cmd+='sed -i  "s#variable .* pressure .*#variable        pressure equal {}#g" {}/in.pressure\n'.format(P_str,name_sim+args.left)
        cmd+='sed -i  \"s#variable.*temperature.*#variable        temperature equal {}#g\" {}/in.temp\n'.format(T_str,name_sim+args.left)
        cmd+='sed -i  \"s#thermo_style.*#thermo_style    custom step temp pe etotal epair emol press lx ly lz vol pxx pyy pzz pxy pxz pyz enthalpy#g\" {}/in.setup\n'.format(name_sim+args.left)

        os.system(cmd)



        if args.initial_equilibration_steps>0 and abs(I)==0:
            # Run equilibration
            cmd  ='sed -i  \"s#run .*#run             {}#g\" {}/start.lmp\n'.format(args.steps_per_sim,name_sim+args.right)
            cmd  +='sed -i  \"s#run .*#run             {}#g\" {}/start.lmp\n'.format(args.steps_per_sim,name_sim+args.left)
            cmd  += '{{\n cd {}\n {} {} -sf omp -in start.lmp\n}}&\n'.format(name_sim+args.left,args.run_cmd,args.lmp_exe)
            cmd  += '{{\n cd {}\n {} {}  -sf omp -in start.lmp\n}}&\n'.format(name_sim+args.right,args.run_cmd,args.lmp_exe)
            cmd  += 'wait\n'.format(name_sim+args.right,args.lmp_exe)
            os.system(cmd)

        # Run simulation
        cmd  ='sed -i  \"s#run .*#run             {}#g\" {}/Restart.lmp\n'.format(args.steps_per_sim,name_sim+args.right)
        cmd  +='sed -i  \"s#run .*#run             {}#g\" {}/Restart.lmp\n'.format(args.steps_per_sim,name_sim+args.left)

        cmd += '{{\n cd {}\n {} {} -sf omp -in Restart.lmp\n}}&\n'.format(name_sim+args.left,args.run_cmd,args.lmp_exe)
        cmd += '{{\n cd {}\n {} {}  -sf omp -in Restart.lmp\n}}&\n'.format(name_sim+args.right,args.run_cmd,args.lmp_exe)
        cmd += 'wait\n'
        os.system(cmd)

    # Gather result
    log_Liquid = np.loadtxt(name_sim+args.right+'/vol_enthalpy.dat')
    log_IceIh  = np.loadtxt(name_sim+args.left+'/vol_enthalpy.dat')

    # #Number of atoms
    # n_iceIh  = int(os.popen(' grep -nr atoms {} | grep Loop'.format(name_sim+args.left+'/log.lammps')).read().split()[-2])
    # n_liquid = int(os.popen(' grep -nr atoms {} | grep Loop'.format(name_sim+args.right+'/log.lammps')).read().split()[-2])

#    log_Liquid = extract_form_log(name_sim+args.right+'/vol_enthalpy.dat')
#    log_IceIh  = extract_form_log(name_sim+args.left+'/vol_enthalpy.dat')
 
    
    production=int(len(log_IceIh[:,0])*args.percent_equilibration/100.)
    h_iceIh  = np.mean(log_IceIh[:,2][production:])#/n_iceIh
    v_iceIh  = np.mean(log_IceIh[:,1][production:])#/n_iceIh
    h_liquid = np.mean(log_Liquid[:,2][production:])#/n_liquid
    v_liquid = np.mean(log_Liquid[:,1][production:])#/n_liquid
    
    # Change in volume from iceIh to Liquid
    dv=v_liquid-v_iceIh #Å^3
    dv_si = dv*1E-10**3 #m^3
    
    # Change in enthalpy from iceIh to Liquid
    dh=h_liquid-h_iceIh #kcal/mol
    dh_si = dh*6.9477E-21

    DPDT_si = (dh_si)/(dv_si*T)

    # Derivative
    DPDT_atm=DPDT_si/101325
    DTDP_atm=1./DPDT_atm

    I = I + int(np.sign(dt))

    # Return depending on integration variable
    if args.integration_variable=='P':
        return DTDP_atm
    elif args.integration_variable=='T':
        return DPDT_atm


    
# Set initial point
if args.initial_TP[0]  is None:
    T = np.array([float(os.popen('grep temperature {}/{}/in.temp'.format(args.initial_point_folder,args.left)).read().split()[-1])])
    P = np.array([float(os.popen('grep " pressure " {}/{}/in.pressure'.format(args.initial_point_folder,args.left)).read().split()[-1])])
else:
    T=np.array([args.initial_TP[0]])
    P=np.array([args.initial_TP[1]])


    
# Run integration
if args.integration_variable=='P':   
    if P[0]<args.end_variable:
        dt=args.step
    else:
        dt=-args.step
    t=np.arange(P[0],args.end_variable,dt)
    y=rungekutta4(fn,T,t)
    last=fn(np.array(y[-1]),t[-1])
    
if args.integration_variable=='T':
    if T[0]<args.end_variable:
        dt=args.step
    else:
        dt=-args.step
    t=np.arange(T[0],args.end_variable,dt)
    y=rungekutta4(fn,P,t)
    last=fn(np.array(y[-1]),t[-1])

