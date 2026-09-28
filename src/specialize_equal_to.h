#pragma once

#include <cstddef>
#include <functional>
#include <utility>
#include <variant>
#include <vector>

#define SPECIALIZE_EQ(t) namespace std { \
    template<> struct equal_to<t> { bool operator()(const t&, const t&) const; }; } \
    bool std::equal_to<t>::operator()(const t &a, const t &b) const \

template <typename T>
inline auto eq(const T &a, const T &b) -> decltype(std::equal_to<T>{}(a, b))
{
    return std::equal_to<T>{}(a, b);
}

namespace detail
{
template <typename... Types>
struct variant_equal_to_visitor
{
    template <typename U>
    bool operator()(const U &v) const
    {
        const U *p_other = std::get_if<U>(&other);
        if (nullptr == p_other)
            return false;
        return std::equal_to<U>{}(v, *p_other);
    }

    const std::variant<Types...> &other;
};
} //namespace detail

namespace std
{
template <typename First, typename Second>
struct equal_to<pair<First, Second>>
{
    bool operator()(const pair<First, Second> &a, const pair<First, Second> &b) const
    {
        return eq(a.first, b.first) && eq(a.second, b.second);
    }
};

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

template <typename... Types>
struct equal_to<variant<Types...>>
{
    bool operator()(const variant<Types...> &a, const variant<Types...> &b) const
    {
        return std::visit(detail::variant_equal_to_visitor<Types...>{b}, a);
    }
};
} //namespace std
