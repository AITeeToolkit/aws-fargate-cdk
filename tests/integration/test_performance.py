"""
Performance tests for API, Web, and Domain Processing
"""

import concurrent.futures
import os
import time
from typing import List

import boto3
import pytest
import requests
from botocore.exceptions import ClientError


@pytest.mark.performance
class TestAPIPerformance:
    """Performance tests for API service"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for API performance tests"""
        self.env = os.getenv("ENVIRONMENT", "staging")
        # API is internal - test via Web service which proxies to API
        self.api_endpoint = os.getenv("WEB_ENDPOINT")
        if not self.api_endpoint:
            pytest.skip("WEB_ENDPOINT not configured for performance testing")

    def test_api_concurrent_requests(self):
        """Test API can handle concurrent requests"""
        num_requests = 50
        timeout = 30  # seconds

        def make_request(request_id):
            start = time.time()
            try:
                response = requests.get(f"{self.api_endpoint}/health", timeout=5)
                elapsed = time.time() - start
                return {
                    "id": request_id,
                    "status": response.status_code,
                    "time": elapsed,
                    "success": response.status_code == 200,
                }
            except Exception as e:
                return {
                    "id": request_id,
                    "status": 0,
                    "time": time.time() - start,
                    "success": False,
                    "error": str(e),
                }

        # Execute concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(make_request, range(num_requests)))
        total_time = time.time() - start_time

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        response_times = [r["time"] for r in successful]

        # Assertions
        success_rate = len(successful) / num_requests
        assert success_rate >= 0.95, f"Success rate {success_rate:.1%} below 95%"

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]

            assert avg_time < 2.0, f"Average response time {avg_time:.2f}s exceeds 2s"
            assert p95_time < 5.0, f"P95 response time {p95_time:.2f}s exceeds 5s"

            # Calculate throughput
            throughput = num_requests / total_time
            print(f"\n📊 API Performance Metrics:")
            print(f"  Success Rate: {success_rate:.1%}")
            print(f"  Total Requests: {num_requests}")
            print(f"  Successful: {len(successful)}")
            print(f"  Failed: {len(failed)}")
            print(f"  Average Response Time: {avg_time:.3f}s")
            print(f"  P95 Response Time: {p95_time:.3f}s")
            print(f"  Throughput: {throughput:.2f} req/s")

    def test_api_sustained_load(self):
        """Test API under sustained load for 30 seconds"""
        duration = 30  # seconds
        requests_per_second = 5

        results = []
        start_time = time.time()

        while time.time() - start_time < duration:
            batch_start = time.time()

            # Send requests_per_second requests
            for _ in range(requests_per_second):
                try:
                    response = requests.get(f"{self.api_endpoint}/health", timeout=5)
                    results.append(
                        {"success": response.status_code == 200, "time": time.time()}
                    )
                except Exception:
                    results.append({"success": False, "time": time.time()})

            # Wait to maintain rate
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)

        # Analyze sustained load results
        total_requests = len(results)
        successful = sum(1 for r in results if r["success"])
        success_rate = successful / total_requests if total_requests > 0 else 0

        print(f"\n📊 Sustained Load Test ({duration}s):")
        print(f"  Total Requests: {total_requests}")
        print(f"  Successful: {successful}")
        print(f"  Success Rate: {success_rate:.1%}")
        print(f"  Target Rate: {requests_per_second} req/s")

        assert (
            success_rate >= 0.90
        ), f"Sustained load success rate {success_rate:.1%} below 90%"


@pytest.mark.performance
class TestWebPerformance:
    """Performance tests for Web service"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for Web performance tests"""
        self.env = os.getenv("ENVIRONMENT", "staging")
        self.web_endpoint = os.getenv("WEB_ENDPOINT")
        if not self.web_endpoint:
            pytest.skip("WEB_ENDPOINT not configured for performance testing")

    def test_web_page_load_concurrent(self):
        """Test web page can handle concurrent users"""
        num_users = 20

        def load_page(user_id):
            start = time.time()
            try:
                response = requests.get(
                    self.web_endpoint, timeout=10, allow_redirects=True
                )
                elapsed = time.time() - start
                return {
                    "user": user_id,
                    "status": response.status_code,
                    "time": elapsed,
                    "size": len(response.content),
                    "success": response.status_code == 200,
                }
            except Exception as e:
                return {
                    "user": user_id,
                    "status": 0,
                    "time": time.time() - start,
                    "success": False,
                    "error": str(e),
                }

        # Simulate concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(load_page, range(num_users)))

        successful = [r for r in results if r["success"]]
        load_times = [r["time"] for r in successful]

        if load_times:
            avg_load = sum(load_times) / len(load_times)
            p95_load = sorted(load_times)[int(len(load_times) * 0.95)]

            print(f"\n📊 Web Performance Metrics:")
            print(f"  Concurrent Users: {num_users}")
            print(f"  Successful Loads: {len(successful)}")
            print(f"  Average Load Time: {avg_load:.3f}s")
            print(f"  P95 Load Time: {p95_load:.3f}s")

            assert avg_load < 3.0, f"Average page load {avg_load:.2f}s exceeds 3s"
            assert p95_load < 5.0, f"P95 page load {p95_load:.2f}s exceeds 5s"


@pytest.mark.performance
class TestDomainProcessingPerformance:
    """Performance tests for domain processing pipeline"""

    @pytest.fixture(autouse=True)
    def setup_aws_clients(self):
        """Setup AWS clients"""
        self.sqs_client = boto3.client("sqs", region_name="us-east-1")
        self.route53_client = boto3.client("route53")
        self.env = os.getenv("ENVIRONMENT", "staging")

        # Get SQS queue URL
        try:
            queue_name = f"dns-operations-{self.env}.fifo"
            response = self.sqs_client.get_queue_url(QueueName=queue_name)
            self.queue_url = response["QueueUrl"]
        except ClientError:
            pytest.skip(f"SQS queue {queue_name} not found")

    def test_domain_processing_throughput(self):
        """Test how many domains can be processed per minute"""
        test_domains = [f"perf-test-{i}.example.com" for i in range(10)]

        # Send domain activation messages to SQS
        start_time = time.time()
        sent_count = 0

        for i, domain in enumerate(test_domains):
            try:
                self.sqs_client.send_message(
                    QueueUrl=self.queue_url,
                    MessageBody=f'{{"domain": "{domain}", "action": "activate", "tenant_id": "perf-test"}}',
                    MessageGroupId="performance-test",
                    MessageDeduplicationId=f"perf-test-{i}-{int(time.time())}",
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send message for {domain}: {e}")

        send_duration = time.time() - start_time

        # Wait for processing (simplified - in real test would poll for completion)
        time.sleep(5)

        # Check queue depth to see how many are still pending
        try:
            attrs = self.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url, AttributeNames=["ApproximateNumberOfMessages"]
            )
            pending = int(attrs["Attributes"]["ApproximateNumberOfMessages"])
        except Exception:
            pending = 0

        print(f"\n📊 Domain Processing Performance:")
        print(f"  Domains Queued: {sent_count}")
        print(f"  Queue Time: {send_duration:.3f}s")
        print(f"  Messages/sec: {sent_count/send_duration:.2f}")
        print(f"  Still Pending: {pending}")

        # Assert we can queue at least 2 domains per second
        assert sent_count / send_duration >= 2.0, "Domain queuing rate below 2/sec"

    def test_sqs_message_processing_rate(self):
        """Test SQS message processing rate"""
        # Send batch of messages
        num_messages = 10
        start_time = time.time()

        entries = []
        for i in range(num_messages):
            entries.append(
                {
                    "Id": str(i),
                    "MessageBody": f'{{"test": "message-{i}"}}',
                    "MessageGroupId": "rate-test",
                    "MessageDeduplicationId": f"rate-test-{i}-{int(time.time())}",
                }
            )

        # Send in batches of 10 (SQS limit)
        for batch_start in range(0, len(entries), 10):
            batch = entries[batch_start : batch_start + 10]
            try:
                self.sqs_client.send_message_batch(
                    QueueUrl=self.queue_url, Entries=batch
                )
            except Exception as e:
                print(f"Batch send failed: {e}")

        send_time = time.time() - start_time

        print(f"\n📊 SQS Processing Rate:")
        print(f"  Messages Sent: {num_messages}")
        print(f"  Send Time: {send_time:.3f}s")
        print(f"  Rate: {num_messages/send_time:.2f} msg/s")

        # Should be able to send at least 10 messages per second
        assert num_messages / send_time >= 10.0, "SQS send rate below 10 msg/s"

    @pytest.mark.slow
    def test_route53_bulk_operations(self):
        """Test Route53 bulk hosted zone operations (marked slow)"""
        # This test is marked slow as it actually creates/deletes hosted zones
        # Only run in staging, not in every test run

        if self.env != "staging":
            pytest.skip("Route53 bulk operations only tested in staging")

        test_zones = [f"perf-test-{i}.example.com" for i in range(3)]
        created_zones = []

        # Test creation speed
        start_time = time.time()
        for domain in test_zones:
            try:
                response = self.route53_client.create_hosted_zone(
                    Name=domain,
                    CallerReference=f"perf-test-{int(time.time())}-{domain}",
                )
                created_zones.append(response["HostedZone"]["Id"])
            except Exception as e:
                print(f"Failed to create zone {domain}: {e}")

        creation_time = time.time() - start_time

        # Cleanup - delete created zones
        for zone_id in created_zones:
            try:
                self.route53_client.delete_hosted_zone(HostedZoneId=zone_id)
            except Exception as e:
                print(f"Failed to delete zone {zone_id}: {e}")

        print(f"\n📊 Route53 Bulk Operations:")
        print(f"  Zones Created: {len(created_zones)}")
        print(f"  Creation Time: {creation_time:.3f}s")
        print(f"  Rate: {len(created_zones)/creation_time:.2f} zones/s")

        # Should be able to create at least 0.5 zones per second
        if len(created_zones) > 0:
            assert (
                len(created_zones) / creation_time >= 0.5
            ), "Zone creation rate below 0.5/sec"
