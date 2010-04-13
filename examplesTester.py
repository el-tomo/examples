# -*- coding: utf-8 -*-
import os, sys, subprocess
from time import strftime

cwd = os.getcwd();
logDir = cwd + "/../../build/logs";
ndiff = cwd + "/../utils/ndiff"
rootUrl = "http://autotest.bioeng.auckland.ac.nz/opencmiss-build/"

if not os.path.isdir(logDir):
  os.mkdir(cwd + "/../../build")
  os.mkdir(logDir);
compiler = sys.argv[1];
os.putenv('HOME', '/home/autotest')
mpidir = cwd+'/../../../opencmissextras/cm/external/x86_64-linux-debug/mpich2/'+compiler+'/bin'
os.system('python ' + mpidir + '/mpd.py &')
f = open(logDir+'/build.log',"r")
successbuilds = f.read()
f.close()
f = open(logDir+'/build.log',"a")

def testExample(id, path, nodes, input=None, args=None, ndiffDir=None,outputDir=None) :
   global compiler,logDir,successbuilds,f;
   index = successbuilds.find(compiler+'_'+path)
   index = successbuilds.find('|',index)
   if (successbuilds.startswith('success',index+1)) :
     newDir = logDir
     for folder in path.split('/') :
       newDir = newDir + '/' + folder
       if not os.path.isdir(newDir):
         os.mkdir(newDir)
     os.chdir(path)
     if os.path.exists(newDir + "/test"+id+"-" + compiler) :
       os.remove(newDir + "/test"+id+"-" + compiler)
     execPath='bin/x86_64-linux/mpich2/'+compiler+'/'+path.rpartition('/')[2]+'Example-debug'
     if nodes == '1' :
       if input != None :
         inputPipe = subprocess.Popen(["echo", input], stdout=subprocess.PIPE)
         f1 = open(newDir + "/test" + id + "-" + compiler,"w")
         execCommand = subprocess.Popen([execPath], stdin=inputPipe.stdout, stdout=f1,stderr=f1)
         f1.close()
         err = os.waitpid(execCommand.pid, 0)[1]
       elif args==None :
         err=os.system(execPath +" > " + newDir + "/test" + id + "-" + compiler + " 2>&1")
       else :
         err=os.system(execPath + ' ' + args +" > " + newDir + "/test" + id + "-" + compiler + " 2>&1")
     else :
       if input != None :
         inputPipe = subprocess.Popen(["echo", input], stdout=subprocess.PIPE)
         f1 = open(newDir + "/test" + id + "-" + compiler,"w")
         execCommand = subprocess.Popen(["mpiexec","-n",nodes,execPath], stdin=inputPipe.stdout, stdout=f1,stderr=subprocess.PIPE)
         f1.close()
         err = os.waitpid(execCommand.pid, 0)[1]
       elif args==None :
         err=os.system('python ' + mpidir + '/mpiexec.py -n ' + nodes + ' ' + execPath +" > " + newDir + "/test" + id + "-" + compiler + " 2>&1")
       else :
         err=os.system('python ' + mpidir + '/mpiexec.py -n ' + nodes + " " + execPath + ' ' + args+" > " + newDir + "/test" + id + "-" + compiler + " 2>&1")
     if err==0 and ndiffDir != None and outputDir != None :
     	for outputFile in os.listdir(ndiffDir) :
		if outputFile!='.svn' :
       			error=os.system(ndiff + ' --tolerance=1e-10 ' + ndiffDir +'/'+outputFile + ' ' + outputDir +'/'+outputFile + ' >> '  + newDir + "/test" + id + "-" + compiler + " 2>&1")
			if err==0 :
				err=error
     if not os.path.exists(execPath) :
       err=-1
     if err==0 :
       f.write(compiler+'_'+path+'_test|success|'+ strftime("%Y-%m-%d %H:%M:%S")+'\n')
       print "Testing %s%s: <a class='success' href='%slogs_x86_64-linux/%s/test%s-%s'>success</a><br>" %(path,id,rootUrl,path,id,compiler)
     else :
       f.write(compiler+'_'+path+'_test|fail|'+ strftime("%Y-%m-%d %H:%M:%S")+'\n')
       print "Testing %s%s: <a class='fail' href='%slogs_x86_64-linux/%s/test%s-%s'>failed</a><br>" %(path,id,rootUrl,path,id,compiler)
     os.chdir(cwd)
   else :
     f.write(compiler+'_'+path+'_test|fail|'+ strftime("%Y-%m-%d %H:%M:%S")+'\n')
     print "Testing %s%s: <a class='fail'>failed</a> due to build failure<br>" %(path,id)
   return;

#testExample(id='1', path="ClassicalField/AdvectionDiffusion", nodes='1')
testExample(id='1', path="ClassicalField/AdvectionDiffusion/AdvectionDiffusionIO", nodes='1')
testExample(id='1', path="ClassicalField/AdvectionDiffusion/StaticAdvectionDiffusion", nodes='1')
testExample(id='1', path="ClassicalField/Diffusion", nodes='1')
testExample(id='1', path="ClassicalField/DiffusionConstantSource", nodes='1')
#testExample(id='1', path="ClassicalField/Helmholtz", nodes='1',input='4\n4\n0\n1')
testExample(id='1', path="ClassicalField/NonlinearPoisson",nodes='1',input='4\n4\n0\n1')
testExample(id='1', path="ClassicalField/Laplace/AnalyticLaplace", nodes='1', ndiffDir='expected_files', outputDir='.')
testExample(id='1', path="ClassicalField/Laplace/Laplace", nodes='1',args='4 4 0 1') 
testExample(id='2', path="ClassicalField/Laplace/NumberLaplace", nodes='1',args='4 4 0 1')

#testExample(id='1',path="Bioelectrics/Monodomain",nodes='1',input='4\n4\n0\n1')
  
testExample(id='1',path="FluidMechanics/Stokes/ALE",nodes='1',input='\n')
testExample(id='1',path="FluidMechanics/Stokes/Static",nodes='1',input='\n')
testExample(id='1',path="FluidMechanics/Stokes/Dynamic",nodes='1',input='\n')
testExample(id='1',path="FluidMechanics/NavierStokes/ALE",nodes='1',input='\n')
testExample(id='1',path="FluidMechanics/NavierStokes/Static",nodes='1',input='\n')
testExample(id='1',path="FluidMechanics/NavierStokes/Dynamic",nodes='1',input='\n')


testExample(id='1',path="FluidMechanics/Darcy/Static",nodes='1',input='\n')
testExample(id='1',path="FluidMechanics/Darcy/QuasistaticMaterial",nodes='1',input='\n',ndiffDir="expected_results",outputDir="output")
#testExample(id='1',path="FluidMechanics/Darcy/VenousCompartment",nodes='1',input='4\n4\n0\n1')

#testExample(id='1',path="FiniteElasticity/UniAxialExtension",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="FiniteElasticity/TwoElementTriLinear",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="FiniteElasticity/MixedBoundaryConditions",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="FiniteElasticity/TriCubicAxialExtension",nodes='1',input='4\n4\n0\n1')

#testExample(id='1',path="LinearElasticity/2DAnalytic1",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="LinearElasticity/2DPlaneStressLagrangeBasis",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="LinearElasticity/3DAnalytic1",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="LinearElasticity/3DLagrangeBasis",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="LinearElasticity/3DCubicHermiteBasis",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="LinearElasticity/3DLagrangeBasisAnisotropicFibreField",nodes='1',input='4\n4\n0\n1')


# TODO Group them
#testExample(id='1',path="LagrangeSimplexMesh",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="cellml",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="define-geometry-and-export",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="MoreComplexMesh",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="simple-field-manipulation-direct-access",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="SimplexMesh",nodes='1',input='4\n4\n0\n1')
#testExample(id='1',path="TwoRegions",nodes='1',input='4\n4\n0\n1')

f.close()

os.system('python ' + mpidir + '/mpdallexit.py')
