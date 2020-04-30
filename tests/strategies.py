from functools import reduce

import hypothesis.strategies as st

pools = st.lists(  # type: ignore
    st.fixed_dictionaries(
        dict(  # type: ignore
            id=st.integers(min_value=1),
            productId=st.text(),
            productName=st.text(),
            startDate=st.dates().map(lambda d: d.isoformat()),
            endDate=st.dates().map(lambda d: d.isoformat()),
            multiplier=st.integers(min_value=1),
            quantity=st.integers(min_value=-1),
            productAttributes=st.lists(
                st.fixed_dictionaries(
                    dict(  # type: ignore
                        name=st.just("instance_multiplier"),
                        value=st.integers(min_value=1),
                    )
                )
            ),
        )
    )
)

terms = st.lists(
    st.fixed_dictionaries(
        dict(
            translations=st.lists(
                st.fixed_dictionaries({"termsPdfId": st.integers(min_value=0)})
            )
        )
    )
)


def count_terms(terms_list):
    """Count valid terms in terms_list."""
    return reduce(
        lambda a, b: a + 1 if len(b.get("translations", [])) > 0 else a, terms_list, 0
    )


order = st.fixed_dictionaries(
    dict(
        regNumbers=st.lists(
            st.lists(
                st.fixed_dictionaries(dict(regNumber=st.integers(min_value=1))),
                min_size=1,
                max_size=1,
            ),
            min_size=1,
            max_size=1,
        )
    )
)

activation = st.fixed_dictionaries(dict(id=st.integers(min_value=1)))
