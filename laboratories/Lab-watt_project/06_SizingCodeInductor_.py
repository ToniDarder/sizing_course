import scipy
import scipy.optimize
from math import pi, sqrt
import timeit

# Specifications
IL_max=150 # [A] max current
IL_RMS=140 # [A] RMS current
L=150e-6 # [H] Inductance
 
# Assumptions
J=5e6 # [A/m²] Current density
B_mag_max=0.4 # [T] Induction
k_bob=0.33 # [-] winding coefficient

# Physical constants
mu_0=4*3.14e-7 # [SI] permeability

# Reference parameters for scaling laws (E core)
Airon_ref=738e-6    # [m^2] iron surface
A_ref=100.3e-3    # [m] E core dimension
B_ref=73.15e-3    # [m] E core dimension
C_ref=27.5e-3     # [m] E core dimension
D_ref=46.85e-3     # [m] E core dimension
E_ref=59.4e-3     # [m] E core dimension
F_ref=27.5e-3     # [m] E core dimension

M_ref=493e-3  # [kg] 1 E core mass

#Variables d'optimisation
e=10e-3 # [m] airgap
B=.2 # [T] Induction

# Vector of parameters
parameters = [e, B]


# -----------------------
# sizing code
# -----------------------
# inputs: 
# - param: optimisation variables vector 
# - arg: selection of output  
# output: 
# - objective if arg='Obj', problem characteristics if arg='Prt', constraints other else

def SizingCode(param, arg):
    # Variables
    e=param[0] # [m] air gap
    B_mag=param[1] # [T] induction
    
    # Magnetic energy calculation
    E_mag=1/2*L*IL_max**2 # [J] Energy
    A_iron= E_mag*2*mu_0/B_mag**2/2/e # [m^2] Iron surface
    
    # Reluctance and inductance
    Re=2*e/mu_0/A_iron  # [] reluctance
    N=sqrt(L*Re) # [-] turn number
    
    # Wire section & winding surface
    S_w=IL_RMS/J # [m²] 1 wire section area
    S_bob=N*S_w/k_bob # [m^2] winding surface
    
    # E core scaling
    A=A_ref*(A_iron/Airon_ref)**(1/2) # [m] A core dimension
    B=B_ref*(A_iron/Airon_ref)**(1/2) # [m] B core dimension
    C=C_ref*(A_iron/Airon_ref)**(1/2) # [m] C core dimension
    D=D_ref*(A_iron/Airon_ref)**(1/2) # [m] D core dimension
    E=E_ref*(A_iron/Airon_ref)**(1/2) # [m] E core dimension
    F=F_ref*(A_iron/Airon_ref)**(1/2) # [m] F core dimension
    
    M_core =M_ref*(A_iron/Airon_ref)**(3/2) # [kg] one E core mass
    
    # Core winding surface
    A_core_winding=2*D*(B-C)/2
    e_max=0.1*C
    
    # Mass
    M_copper=2*pi*(B+C)/4*N*S_w*7800
    M_total=M_copper+M_core*2
    
        # Objective and contraints
    if arg=='Obj':
        return M_total
    elif arg=='LCA_parameters':
        return [M_copper, M_core*2, 0, 0]
    elif arg=='Prt':
        print("* Optimisation variables:")
        print("           Airgap e = %.2f mm"% (e*1e3))
        print("           Induction B = %.2f T"% (B_mag))
        print("* Components characteristics:")
        print("           Core (2) mass = %.2f kg" % (2*M_core))
        print("           Coil mass = %.2f kg" % M_copper)
        print("           Core dimensions = %.0f x %.0f x %.0f mmm"%((A*1e3,2*E*1e3,2*F*1e3)))
        print("           A_iron = %.0f mm^2"%(A_iron*1e6))
        print("           Number of turns = %i"%(N))
        print("* Constraints (should be >0):")
        print("           Winding  surface margin = %.3f mm²" % ((A_core_winding-S_bob)*1e6))
        print("           Airgap margin = %.3f mm" %((e_max-e)*1e3))
    else:
        return [A_core_winding-S_bob, e_max-e]
