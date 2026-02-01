# { blacklisted_word: test_texts }
bad_samples = {
    "badword1": [
        "b@dw0rd1 ",
        "badw0rd1",
        "Bad-word1!",
        "B@d*w0rd!1",
        "baadword1",
        "b*d*w*rd1",
        "b-a-d-w-o-r-d-1",
    ],
    "badword2": ["badwrd2"],
}

norm_samples = {
    "badword1": [
        "normal message",
        "word1",
    ],
    "badword2": [
        "normal message",
        "banderol",
        "band",
    ],
}
