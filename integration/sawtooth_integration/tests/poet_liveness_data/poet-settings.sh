#!/bin/bash
# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

settings=""
settings="$settings sawtooth.poet.target_wait_time=2"
settings="$settings sawtooth.poet.initial_wait_time=10"
settings="$settings sawtooth.publisher.max_batches_per_block=100"
settings="$settings sawtooth.poet.ztest_maximum_win_deviation=2.5"
settings="$settings sawtooth.poet.ztest_minimum_win_count=1"
settings="$settings sawtooth.poet.population_estimate_sample_size=50"
settings="$settings sawtooth.poet.key_block_claim_limit=100"

echo "$settings"
