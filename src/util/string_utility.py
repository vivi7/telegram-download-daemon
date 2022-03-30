import string, random, re


class StringUtility:


    @staticmethod
    def get_random_id(len):
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choice(chars) for x in range(len))


    @staticmethod
    def extract_urls(text):
        return re.findall("(?P<url>https?://[^\s]+)", text)


    @staticmethod
    def contains_url(text):
        return len(StringUtility.extract_urls(text)) > 0


    @staticmethod
    def match_text(regex, text):
        return re.match(regex, text)

