import contextlib,hashlib,importlib.util,io,json,pathlib,tempfile,unittest,urllib.error,uuid,zipfile
from unittest.mock import patch
MODULE=pathlib.Path(__file__).resolve().parents[1]/'plugins/aqteron/skills/publish-aqteron-app/scripts/zip_direct.py'
spec=importlib.util.spec_from_file_location('zip_direct',MODULE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class UploadTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'app.zip'
  with zipfile.ZipFile(self.path,'w') as z:z.writestr('index.html','counter')
  self.id=str(uuid.uuid4());self.url='https://aqteron.com/api/ai/zip-transfer/browser/'+self.id+'/file';self.ticket='s'*43
 def tearDown(self):self.tmp.cleanup()
 def response(self,**changed):
  b=self.path.read_bytes();r={'transfer_id':self.id,'received_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'status':'receiving',**changed}
  return io.BytesIO(json.dumps(r).encode())
 def run_main(self,error):
  output=io.StringIO()
  with patch.object(m,'upload',side_effect=error),patch('sys.argv',['helper',str(self.path),'--upload-url',self.url,'--upload-ticket',self.ticket]),contextlib.redirect_stderr(output):
   rc=m.main()
  self.assertEqual(rc,2);self.assertNotIn(self.ticket,output.getvalue());self.assertNotIn(self.url,output.getvalue());return json.loads(output.getvalue())
 def test_one_binary_put(self):
  class Opener:
   def open(inner,req,timeout):
    self.assertEqual(req.method,'PUT');self.assertEqual(req.data,self.path.read_bytes());self.assertEqual(req.get_header('X-aqteron-upload-ticket'),self.ticket);self.assertEqual(timeout,120);return self.response()
  with patch.object(m.urllib.request,'build_opener',return_value=Opener()) as builder:
   r=m.upload(self.path,self.url,self.ticket);self.assertEqual(r['transfer_id'],self.id);self.assertIsInstance(builder.call_args.args[0],m.NoRedirect)
 def test_receipt_requires_same_transfer_and_hash(self):
  for changed in [{'transfer_id':str(uuid.uuid4())},{'sha256':'0'*64},{'received_bytes':1},{'status':'completed'}]:
   with self.subTest(changed=changed),patch.object(m.urllib.request,'build_opener') as b:
    b.return_value.open.return_value=self.response(**changed)
    with self.assertRaises(ValueError):m.upload(self.path,self.url,self.ticket)
 def test_destination_guards(self):
  for url in [self.url.replace('https:','http:'),self.url.replace('aqteron.com','aqteron.com.evil.invalid'),self.url+'?ticket='+self.ticket,self.url+'#fragment',self.url.replace('aqteron.com','u:p@aqteron.com'),self.url.replace('/browser/','/')]:
   with self.subTest(url=url),patch.object(m.urllib.request,'build_opener') as b:
    with self.assertRaises(ValueError):m.upload(self.path,url,self.ticket)
    b.assert_not_called()
 def test_idempotency_key_is_not_ticket(self):
  with self.assertRaises(ValueError):m.upload(self.path,self.url,str(uuid.uuid4()))
 def test_no_redirect(self):self.assertIsNone(m.NoRedirect().redirect_request(None,None,307,'',{},'https://other.invalid'))
 def test_proxy_403_classified(self):self.assertEqual(self.run_main(urllib.error.URLError('Tunnel connection failed: 403 Forbidden'))['error'],'network_egress_blocked')
 def test_server_403_not_classified_as_network(self):
  e=urllib.error.HTTPError(self.url,403,'Forbidden',{},io.BytesIO(b'{"error":"upload_ticket_invalid"}'))
  self.assertEqual(self.run_main(e)['error'],'upload_ticket_invalid')
 def test_unsanitized_server_message_hidden(self):
  e=urllib.error.HTTPError(self.url,500,'Failure',{},io.BytesIO(json.dumps({'error':self.url+self.ticket}).encode()))
  self.assertEqual(self.run_main(e)['error'],'http_upload_failed')
 def test_timeout(self):self.assertEqual(self.run_main(TimeoutError())['error'],'network_timeout')
 def test_wrapped_timeout(self):self.assertEqual(self.run_main(urllib.error.URLError(TimeoutError()))['error'],'network_timeout')
 def test_json_diagnostic_is_not_egress_signal(self):
  e=urllib.error.HTTPError(self.url,403,'Forbidden',{},io.BytesIO(b'{"error":"upload_ticket_invalid","message":"not a network egress failure"}'))
  self.assertEqual(self.run_main(e)['error'],'upload_ticket_invalid')
 def test_token_shaped_error_is_hidden(self):
  e=urllib.error.HTTPError(self.url,403,'Forbidden',{},io.BytesIO(json.dumps({'error':self.ticket}).encode()))
  self.assertEqual(self.run_main(e)['error'],'http_upload_failed')
 def test_error_body_read_failure(self):
  class Broken:
   def read(self,*args):raise OSError('failure')
   def close(self):pass
  e=urllib.error.HTTPError(self.url,500,'Error',{},Broken())
  self.assertEqual(self.run_main(e)['error'],'http_upload_failed')
if __name__=='__main__':unittest.main()
