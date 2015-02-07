"""
Wrap BGFX shader compiler as fips code generator (for code-embedded shaders)
See: bgfx/scripts/shader_embeded.mk
"""
Version = None

import os
import platform
import genutil
import tempfile
import subprocess
from mod import log

#-------------------------------------------------------------------------------
def get_shaderc_path() :
    """find shaderc compiler, fail if not exists"""
    proj_path = os.path.dirname(os.path.abspath(__file__))
    os_name = platform.system().lower()
    shaderc_path = '{}/../bgfx/tools/bin/{}/shaderc'.format(proj_path, os_name)
    shaderc_path = os.path.normpath(shaderc_path)
    if not os.path.isfile(shaderc_path) :
        log.error("bgfx shaderc executable not found, please run 'make tools' in bgfx directory")
    return shaderc_path

#-------------------------------------------------------------------------------
def get_include_path() :
    """return the global shader header search path"""
    proj_path = os.path.dirname(os.path.abspath(__file__))
    include_path = '{}/../bgfx/src'.format(proj_path)
    include_path = os.path.normpath(include_path)
    if not os.path.isdir(include_path) :
        log.error("could not find bgfx shader include search path at '{}'".format(include_path))
    return include_path

#-------------------------------------------------------------------------------
def get_basename(input_path) :
    return os.path.splitext(os.path.basename(input_path))[0]

#-------------------------------------------------------------------------------
def run_shaderc(input_file, out_tmp, platform, type, subtype, bin_name) :
    cmd = [ 
        get_shaderc_path(),
        '-i', get_include_path(),
        '--platform', platform,
        '--type', type
    ]
    if subtype :
        cmd.extend(['-p', subtype])
    if platform == 'windows' :
        cmd.extend(['-O', '3'])
    cmd.extend([
        '-f', input_file,
        '-o', out_tmp,
        '--bin2c', bin_name
    ])
    print(cmd)
    subprocess.call(cmd)

#-------------------------------------------------------------------------------
def generate(input_file, out_src, out_hdr, args) :
    """
    :param input:       bgfx .sc file
    :param out_src:     must be None
    :param out_hdr:     path of output header file
    """

    # source to bgfx shader compiler
    shaderc_path = get_shaderc_path()
    include_path = get_include_path()
    basename = get_basename(input_file)

    # call shader 3 times for glsl, dx9, dx11 into tmp files
    out_glsl = tempfile.mktemp(prefix='bgfx_glsl_shaderc_')
    out_dx9  = tempfile.mktemp(prefix='bgfx_dx9_shaderc_')
    out_dx11 = tempfile.mktemp(prefix='bgfx_dx11_shaderc_')

    # FIXME: the HLSL compiler is only supported on Windows platforms,
    # thus we would get incomplete .bin.h files on non-windows platforms...
    # what to do about this:

    run_shaderc(input_file, out_glsl, 'linux', args['type'], None, basename+'_glsl')
    run_shaderc(input_file, out_dx9, 'windows', args['type'], 
                'vs_3_0' if args['type'] == 'vertex' else 'ps_3_0', basename+'_dx9')
    run_shaderc(input_file, out_dx11, 'windows', args['type'],
                'vs_4_0' if args['type'] == 'vertex' else 'ps_4_0', basename+'_dx11')

    # TODO: merge output temp files into 
