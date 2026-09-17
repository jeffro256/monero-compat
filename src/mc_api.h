#pragma once

#ifdef __cplusplus
#define MC_EXTERNC extern "C"
#else
#define MC_EXTERNC
#endif

#if defined(_WIN32) || defined(__CYGWIN__)
#define MC_VISIBILITY __declspec(dllexport)
#else
#define MC_VISIBILITY __attribute__ ((visibility ("default")))
#endif

#define MC_API_EXPORT MC_EXTERNC MC_VISIBILITY
