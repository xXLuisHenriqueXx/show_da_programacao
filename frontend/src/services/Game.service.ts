import { api } from "./Api.service";

export interface IQuestion {
  id: number;
  text: string;
  options: string[];
  prize: number;
  currency: string;
}

export interface IAnswerResponse {
  result: string;
  correct: boolean;
  accumulated_prize: string;
  explanation: string;
  game_status: string;
}

export const gameService = {
  start: async () => {
    const response = await api.post("/start", {});
    const status = response.status;
    const uuid = response.data.uuid;

    return { status, uuid };
  },

  getNextQuestion: async (uuid: string) => {
    const response = await api.get(`/question/${uuid}`);
    const status = response.status;
    const question: IQuestion = response.data;

    console.log(status);

    return { status, question };
  },

  answerQuestion: async (uuid: string, option_index: number) => {
    const response = await api.post(`/answer/${uuid}`, { option_index });
    const status = response.status;
    const answer: IAnswerResponse = response.data;

    return { status, answer };
  },

  reset: async (uuid: string) => {
    const response = await api.post(`/reset/${uuid}`, {});
    const status = response.status;

    return { status };
  },

  nextLevel: async (uuid: string) => {
    const response = await api.post(`/next-level/${uuid}`, {});
    const status = response.status;

    return { status };
  },

  nextLevelStatus: async (uuid: string) => {
    const response = await api.get(`/next-level/${uuid}/status`);
    const status = response.status;
    const game_status = response.data.status;

    return { status, game_status };
  },
};
