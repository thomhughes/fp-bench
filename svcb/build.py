from . import benchmark
from . import schema
import os

def generateCMakeDecls(benchmarkObjs, sourceRootDir, supportedArchitecture):
  """
    Returns a string containing CMake declarations
    that declare the benchmarks in the list ``benchmarkObjs``.
  """
  assert isinstance(benchmarkObjs, list)
  assert os.path.exists(sourceRootDir)
  assert os.path.isdir(sourceRootDir)
  declStr = "# Autogenerated. DO NOT MODIFY!\n"
  for b in benchmarkObjs:
    assert isinstance(b.name, str)
    assert isinstance(b, benchmark.Benchmark)

    benchmarkArchitectures = None
    if isinstance(b.architectures, str):
      assert b.architectures == 'any'
      benchmarkArchitectures = {'any'}
    else:
      benchmarkArchitectures = b.architectures

    for arch in benchmarkArchitectures:
      declStr += "####\n"
      targetName = '{}.{}'.format(b.name, arch)
      if arch != 'any' and arch != supportedArchitecture:
        # Architecture not supported
        declStr += 'message(STATUS "Compiler cannot build target {}")\n'.format(targetName)
        continue

      # Emit ``add_executable()``
      declStr += "add_executable({target_name}\n".format(target_name=targetName)
      # FIXME: Need to put in absolute path
      for source in b.sources:
        declStr += "  {source_file}\n".format(source_file=os.path.join(sourceRootDir, source))
      declStr += ")\n"
      # Emit linking info
      declStr += "target_link_libraries({target_name} PRIVATE {libs})\n".format(
        target_name=targetName,
        libs="svcomp_runtime")
      # Emit custom macro defintions
      if len(b.defines) > 0:
        declStr += "target_compile_definitions({target_name} PRIVATE\n".format(
          target_name=targetName)
        for macroDefine in b.defines:
          assert isinstance(macroDefine, str)
          declStr += "  {}\n".format(macroDefine)
        declStr += ")\n"
      # Emit compiler flags
      lang_ver = b.language.replace('+','X').upper()
      declStr += "target_compile_options({target_name} PRIVATE ${{SVCOMP_STD_{lang_ver}}})\n".format(
        target_name=targetName,
        lang_ver= lang_ver,
        arch = arch.upper()
      )
  return declStr

