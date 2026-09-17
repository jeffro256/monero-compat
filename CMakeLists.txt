# Monero minimum CMake version requirements
cmake_minimum_required(VERSION 3.10)

# Monero CXX standard requirements
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_subdirectory(${MONERO_ROOT_DIR} monero)

project(monero_compat)
add_subdirectory(src)
