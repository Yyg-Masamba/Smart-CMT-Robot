# * @author        Pea Masamba <comelmuewa831@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   Smart-CMT-Robot
# * Copyright ©peamasamba All rights reserved

# Base Docker Using Debian 12 (Bookworm), Python 3.11.6 and Built In Pip
## With Built in Pip Package
FROM yasirarism/misskaty-docker:ubuntu23.10
## Without Built in Pip Package
# FROM yasirarism/misskaty-docker:free

# Set Hostname
ENV HOSTNAME yasir-server
# Copy Files
COPY . .
# Instal pip package
# RUN pip3 install --no-cache-dir -r requirements.txt
# Set CMD Bot
CMD ["bash", "start.sh"]
