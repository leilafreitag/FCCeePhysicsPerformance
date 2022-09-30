path=/afs/cern.ch/user/a/afehr/FCCAnalyses 	# Default one

cd case-studies/flavour/

export PYTHONPATH=$path:$PYTHONPATH
export LD_LIBRARY_PATH=$path/install/lib:$LD_LIBRARY_PATH
export ROOT_INCLUDE_PATH=$path/install/include:$ROOT_INCLUDE_PATH
cd dataframe/
source ./localSetup.sh
rm -rf build install
mkdir build install
cd build/
cmake .. -DCMAKE_INSTALL_PREFIX=../install -DFCCANALYSES_INCLUDE_PATH=/afs/cern.ch/user/a/afehr/FCCAnalyses_kunal/install/include/FCCAnalyses
make install
