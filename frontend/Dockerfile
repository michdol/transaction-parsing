FROM node:22.12-alpine

WORKDIR /src

COPY package.json ./
RUN npm install

COPY ./* /src

EXPOSE 5173

CMD ["npm", "run", "dev"]
