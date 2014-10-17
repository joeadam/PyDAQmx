import DAQmxFunctions
from DAQmxFunctions import *
import ctypes
import numpy as np

# Create a list of the name of the function that have GetDev ain their names
# All the function of this list will be converted to properties of the Device object
# The name of the method will be the same name as the name of the DAQmx function without the 
# the DAQmx in front of the nameGetDev
device_function_list = [name for name in function_dict.keys() if "GetDev" in name]
#and\         


class Device():
    def __init__(self, devicename):
        self.devicename = devicename
        
    def __repr__(self):
        if self.devicename:
            return "Device %s"%self.devicename
        else:
            return "Err...."
    # Dynamically creates the method from the task_function_list
    for function_name in device_function_list:
        name = function_name[11:] # remove the DAQmxGetDev in front of the name
        
        func = getattr(DAQmxFunctions, function_name) # This line checks whether function name exists
        arg_names = function_dict[function_name]['arg_name']
        arg_types = function_dict[function_name]['arg_type']
        
        doc = 'T.%s(%s) -> error.' %(name, ', '.join(arg_names[1:]))
        
        if arg_types[1] == ctypes.c_char_p:
            cmd = """@property
def {0}(self):
            "{2}"
            return self.GenericCharProperty({1})""".format(name, function_name, doc)
            fullcmd = cmd.format()
        elif arg_types[1] == ctypes.POINTER(ctypes.c_double) and len(arg_types) == 2:
            cmd = """@property
def {0}(self):
            "{2}"
            return self.GenericFloat64Property({1})""".format(name, function_name, doc)
        elif arg_types[1] == ctypes.POINTER(ctypes.c_double) and len(arg_types) == 3:
            cmd = """@property
def {0}(self):
            "{2}"
            return self.GenericFloat64ArrayProperty({1})""".format(name, function_name, doc)
        elif arg_types[1] == ctypes.POINTER(ctypes.c_uint32):
            cmd = """@property
def {0}(self):
            "{2}"
            return self.GenericUint32({1})""".format(name, function_name, doc)
        else:
            cmd = """@property
def {0}(self):
            "{1}"
            return None""".format(name, doc)
        
        exec(cmd)    
    del function_name, name, func, arg_names, doc
    
    def GenericCharProperty(self, funcname):
        buflen = 500
        charbuffer = ctypes.create_string_buffer(buflen)
        cmd = '{0}(self.devicename, charbuffer, buflen)'.format(funcname.func_name)
        exec(cmd)
        
        return charbuffer.value

    def GenericFloat64Property(self, funcname):
        doublevalue = ctypes.c_double(0)
        cmd = '{0}(self.devicename, ctypes.byref(doublevalue))'.format(funcname.func_name)
        exec(cmd)
        return doublevalue.value
    
    def GenericFloat64ArrayProperty(self, funcname):
        buflen = 30
        buf = np.zeros( (buflen,), dtype=np.float64)
        buf[:] = np.NAN
        cmd = '{0}(self.devicename, buf.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),buflen)'.format(funcname.func_name)
        exec(cmd)
        #Remove the non-used itesm from the array
        return buf[np.invert(np.isnan(buf))].tolist()
        
        
    
    def GenericUint32(self, funcname):
        uint32value = ctypes.c_uint32(0)
        cmd = '{0}(self.devicename, ctypes.byref(uint32value))'.format(funcname.func_name)
        exec(cmd)
        return uint32value.value
    
del device_function_list