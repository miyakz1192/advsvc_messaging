#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import traceback
import uuid
from record import *
from messaging import *


# LLMInstanceServiceに要求を行うサービスの基底クラス
# LLMInstanceServiceを使ううえで検討が必要な機能をベースとして実装してある
# このパッケージをimportする前にmessaging配下にパスを通しておく
# 例：
# settting of import messaging
# sys.path.append("messaging")
# from messaging import *
class LLMMediatorBase:
    #
    # 具象クラスでオーバーライドするべきメソッド
    # 

    # サービスへの要求キューからリクエストをgetした際にそれが許容されるものかどうかを判定する
    # 許容される・・・True、されない・・・False
    def is_acceptable_request(self, rec):
        #sample impl
        # if len(rec.in_text) <= 50:
        #     print("INFO: in_text is too short. skip ask to llm")
        #     return False
        return True

    # サービスへの要求キューからメッセージを取り出し、返す
    def get_from_req_queue(self):
        # impl sample. just get record and return this
        # return Text2AdviceServiceReqMessaging().connect_and_basic_get_record()
        pass

    # LLMから結果を受け取り、サービスの結果返却キューにメッセージをpublishする
    def publish_to_res_queue(self, rec):
        # impl sample. just publish record to res queue.
        # Text2AdviceServiceResMessaging().connect_and_basic_publish_record(rec)
        pass
    
    # LLMInstanceから結果が帰ってこなかったレコードを、サービスの要求キューに入れなおす
    def publish_to_req_queue(self, rec):
        # impl sample. jush publish record to req queue
        # Text2AdviceServiceReqMessaging().connect_and_basic_publish_record(rec)
        pass

    # デフォルトの指示テキストを設定する
    def set_default_instruction(self):
        self.default_instruction = "LLMへの指示文章をここに具体的に記載する"

    # LLMInstanceServiceから処理が帰ってきた後、復帰値として、
    # サービス返却キューに返すレコードを作る
    # 引数にサービス要求キューに来たoriginal_recordが渡されるので、それに結果を代入して返す
    # record種別によってメンバーの名前が変わるため、個別実装になる。
    def _make_response_record(self, original_record, llm_output_text):
        # impl sample.
        #original_record.advice_text = advice_text
        #rec = original_record

        # default impl is just returning original_record. rewrite this
        rec = original_record
        return rec

    # LLMInstanceに渡す入力テキスト(input_example)を生成する
    # たいていの場合、サービスへの要求キューに来たrecordが
    # ネタになるため、それを入力として受け取り処理する
    def _make_llm_input_text(self, rec):
        # impl sample.
        # return rec.in_text #要求レコード内のin_text(会話の文字起こし結果)

        # default impl is just void string. rewrite it.
        return ""

    #
    # 具象クラスでオーバーライド不要のメソッド
    # 
    def __init__(self):
        self.default_instruction = "LLMへの指示文章"
        # 要求リトライ用の一時保存リスト
        self.retry_target = []
        self.wait_sec = 10
        self.timed_out_counter_max = 360
        self.set_default_instruction()

    def sleep_wait(self):
        #TODO: FIXME: ランダム性が必要
        time.sleep(self.wait_sec)

    def is_timed_out_to_llminstance(self, timed_out_counter):
        # ある時間経過しても結果が帰って来ない場合
        # 規定実装では、wait_sec = 10 * timed_out_counter_max = 360の3600秒で約1時間待つ
        if timed_out_counter > self.timed_out_counter_max:
            return True
        return False

    def main_loop(self):
        while True:
            try:
                self.unit_work()
            except Exception as e:
                print(f"An error occurred while unit work: {e}")
                traceback.print_exc()

            self.sleep_wait()

    def _make_response_and_publish(self, original_record, llm_output_text):
        print("INFO: _make_response_and_publish")
        rec = self._make_response_record(original_record, llm_output_text)
        self.publish_to_res_queue(rec)

    def retry(self):
        if len(self.retry_target) == 0:
            return

        print("INFO: retry start")
        for rec in self.retry_target:
            print(f"INFO: -> {rec.id}")
            self.publish_to_req_queue(rec)

        self.retry_target = []
        print("INFO: retry end")

    def unit_work(self):
        print("Getting new req from queue")
        rec = self.get_from_req_queue()
        if rec is None:
            self.retry()
            return

        if self.is_acceptable_request(rec) == False:
            return

        input_text_to_llm = self._make_llm_input_text(rec)
        llm_output_text = self.ask_to_llm(input_text_to_llm)
        if llm_output_text is None:
            # append to retry_list
            self.retry_target.append(rec)
            return

        self._make_response_and_publish(rec, llm_output_text)
        print("INFO: unit work end")

    def ask_to_llm(self, input_text):
        return self._ask_to_llm_core(input_text)

    def _ask_to_llm_core(self, input_text):
        timed_out_counter = 0
        print("INFO: ask to llm")
        rec = LLMInstanceRecord(str(uuid.uuid4()), self.default_instruction, input_text)
        LLMInstanceReqMessaging().connect_and_basic_publish_record(rec)
        while True:
            try:
                print("INFO: waiting for llm")
                recv = LLMInstanceResMessaging().connect_and_basic_get_record()
                if recv is None:
                    print("INFO: no message")
                    self.sleep_wait()
                    timed_out_counter += 1
                    # ある時間経過しても結果が帰って来ない場合
                    if self.is_timed_out_to_llminstance(timed_out_counter):
                        print("INFO: timed out")
                        return None

                    continue

                if recv.id == rec.id:
                    print(f"INFO: got a message {recv.result}")
                    return recv.result
                else:
                    #TODO: FIXME: いまだとゴミがあるケースだとタイムアウトしない。TTLの仕組み必要
                    print(f"INFO: got a message but not eq ident(got message was not to mine. this must be received by other llm_mediator instance) {recv.id} != {rec.id}")
                    LLMInstanceResMessaging().connect_and_basic_publish_record(recv)

                self.sleep_wait()
            except Exception as e:
                print(f"An error occurred while unit work: {e}")
                traceback.print_exc()
