#pragma once

#include <cstddef>
#include <functional>
#include <utility>
#include <vector>

#define SPECIALIZE_EQ(t) namespace std { \
    template<> struct equal_to<t> { bool operator()(const t&, const t&) const; }; } \
    bool std::equal_to<t>::operator()(const t &a, const t &b) const \

template <typename T>
inline auto eq(const T &a, const T &b) -> decltype(std::equal_to<T>{}(a, b))
{
    return std::equal_to<T>{}(a, b);
}

namespace std
{
template <typename value_type, typename alloc>
struct equal_to<vector<value_type, alloc>>
{
    bool operator()(const vector<value_type, alloc> &a, const vector<value_type, alloc> &b) const
    {
        if (a.size() != b.size())
            return false;
        for (std::size_t i = 0; i < a.size(); ++i)
            if (!eq(a[i], b[i]))
                return false;
        return true;
    }
};

template <typename First, typename Second>
struct equal_to<pair<First, Second>>
{
    bool operator()(const pair<First, Second> &a, const pair<First, Second> &b) const
    {
        return eq(a.first, b.first) && eq(a.second, b.second);
    }
};
} //namespace std
