## to build:
#
# docker build -t fcli .
#
## to run:
#
# docker run --rm -it -v ~/.fcli:/.fcli fcli [...]
#
# -v adds a mapping so that your ~/.fcli is accessible in the container
# fcli is the image to run
# [...] are the arguments to the fcli command

# use the latest Alpine-based Python 3.x base image
FROM python:3-alpine 

# create a user account for using fcli
RUN adduser fcli -D -h /fcli 

# install fcli
RUN pip install fcli

# set the HOME environment variable
ENV HOME /fcli

# set the working directory
WORKDIR /fcli

# use an unprivileged account to run fcli
USER fcli

# set the default command to "fcli"
ENTRYPOINT [ "fcli" ]

# if the user doesn't specify any arguments, show --help
CMD [ "--help" ]
