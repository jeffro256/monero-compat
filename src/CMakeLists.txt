set(monero_compat_sources
    mc_init.cpp
    PendingTx.cpp)

include_directories("${MONERO_ROOT_DIR}/external/mx25519/include")

find_path(TX_BUILDER_H "tx_builder.h" "${MONERO_ROOT_DIR}/src/wallet")

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
if (TX_BUILDER_H)
target_compile_definitions(monero_compat
    PRIVATE
        -DHAVE_TX_BUILDER)
endif()
