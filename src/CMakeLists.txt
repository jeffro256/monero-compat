set(monero_compat_sources
    mc_init.cpp
    PendingTx.cpp)

add_library(monero_compat
    SHARED # Shared library so Python can use its symbols
    ${monero_compat_sources}
    )
target_link_libraries(monero_compat
    wallet)
target_include_directories(monero_compat
    PRIVATE
    "${MONERO_ROOT_DIR}/contrib/epee/include/"
    "${MONERO_ROOT_DIR}/external/"
    "${MONERO_ROOT_DIR}/external/easylogging++"
    "${MONERO_ROOT_DIR}/src/")
