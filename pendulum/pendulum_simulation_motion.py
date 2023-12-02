from scipy.integrate import odeint
import numpy as np
import scipy 

def initiate_simulation(length, mass,theta0,omega0,g=9.8,debut = 0, fin =40,nb_points = 100, lbd = 0,neon=False,line_length=10,axes=False):
    d= {}
    d['length']=length       #longueur du fil du pendule
    d['mass']=mass           #masse
    d['theta0']=theta0       #angle initial
    d['omega0']=omega0       #vitesse angulaire initiale
    d['g']=g                 #acceleration pesanteur
    d['debut']=debut         #temps début simulation
    d['fin']=fin             #temps fin simuation
    d['nb_points']=nb_points #nb points simulation
    d['lambda']= lbd         #frottements
    d['neon'] = neon         #neon 
    d['line_length'] = line_length #longueur du fil du pendule dans la simulation
    d['axes'] = axes         #axes
    return d

def simple_pendulum_ODE(y,t,g,length, lbd = 0, m = 1): #d est le dictionnaire renvoyé par initiate_simulation
    theta, omega = y
    dydt = [omega, -(g/length)*(np.sin(theta)) - omega*lbd/m]
    return dydt

def find_solution(d):
    t = np.linspace(d['debut'],d['fin'],d['nb_points'])
    solution = odeint(simple_pendulum_ODE, (d['theta0'],d['omega0']), t, args=(d['g'],d['length'], d['lambda'], d['mass'])) #résolution avec odeint
    return t, solution

def find_energie(solution,d):
    energie_cin = (1/2)*d['mass']*(d['length']**2)*(solution[:,1]**2)
    energie_pot = d['mass']*d['g']*d['length']*(1-np.cos(solution[:,0]))
    return energie_cin,energie_pot

def f(x,n):
    if -n<=x<=n:
        return x
    else :
        return np.mod(x,n)