from setuptools import setup

if __name__ == "__main__":
    setup(name="eggutils",
        version="0.0.1",
        license="BSD",
        description="A set of utilities to create/manipulate eggs",
        author="David Cournapeau",
        author_email="cournape@gmail.com",
        entry_points= {
            "console_scripts": [
                "make-dll-egg = eggutils.eggutils:wrap_main"
                ]
        },
        packages=["eggutils"])
