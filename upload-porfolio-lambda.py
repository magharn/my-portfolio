import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-west-2:647579903866:portfolio-deployPortfolio-topic')

    # Follwing code is executed when run this program manually
    location = {
        "bucketName" : 'portfoliobuild.sergiogtz.info',
        "objectKey" : 'portfoliobuild.zip'
    }

    try:
        s3 = boto3.resource('s3')

        job = event.get("CodePipeline.job")

        print('This is the job: ')
        print(type(job))
        print(str(job))

        # Follwing if statment executes code when CodePipeline
        # has been activated
        if job and 	len(job['data']['inputArtifacts']) > 0 :
        	location = (job['data']['inputArtifacts'])[0]['location']['s3Location']

        print("Building portfolio from: " )
        print(str(location))

        portfolio_bucket = s3.Bucket('portfolio.sergiogtz.info')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = io.BytesIO()

        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType' : mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject="Portfolio deployed", Message="Portfolio deployed successfully!.")

        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId = job["id"])
    except:
        topic.publish(Subject="Portfolio deploy failed", Message="The portfolio was not deployed successfully!.")
        raise

    return 'portfolio has been deployed!'
